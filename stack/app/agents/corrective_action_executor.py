from typing import List, TypedDict, Optional, Dict, Any, cast
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, HumanMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph, START
from langchain.schema import Document
from stack.app.core.datastore import get_checkpointer


class GraphState(TypedDict):
    """Represents the state of the CRAG graph."""
    messages: List[BaseMessage]
    question: str
    generation: str
    web_search_needed: bool  
    documents: List[Document]
    iteration_count: int

def get_crag_executor(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    system_prompt: str,
    web_search_tool=None,
    question_rewriter_prompt: Optional[str] = None,
    max_corrective_iterations: int = 3,
    enable_web_search: bool = True,
    relevance_threshold: float = 0.7,
):
    """Create a CRAG executor with proper message handling."""
    
    # Only use LCEL chain for final generation
    generation_prompt = ChatPromptTemplate.from_template(
        "{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    generation_chain = generation_prompt | llm | StrOutputParser()

    async def retrieve(state: GraphState) -> GraphState:
        """Retrieve documents with proper message handling."""
        docs = await retriever.aget_relevant_documents(state["question"])
        
        # Create retrieval message
        retrieval_msg = AIMessage(
            content="",
            additional_kwargs={
                "action": {
                    "type": "retrieval",
                    "documents": [
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        }
                        for doc in docs
                    ]
                }
            }
        )
        
        return {
            **state,
            "documents": docs,
            "messages": state["messages"] + [retrieval_msg]
        }

    async def grade_documents(state: GraphState) -> GraphState:
        """Grade documents using direct message invocation."""
        filtered_docs = []
        needs_web_search = False
        grades = []
        
        grading_messages = []
        
        for doc in state["documents"]:
            # Create grading prompt messages
            messages = [
                SystemMessage(content="""You are an expert at evaluating document relevance.
                    Rate the relevance of retrieved documents to the user's question on a scale of 0.0 to 1.0.
                    - 1.0: Perfectly relevant, directly answers the question
                    - 0.7: Highly relevant, contains most of the needed information
                    - 0.5: Moderately relevant, contains some useful information
                    - 0.3: Slightly relevant, touches on the topic but doesn't address the question
                    - 0.0: Not relevant at all

                    Return ONLY the numerical score without any explanation."""),
                HumanMessage(content=f"Retrieved document: {doc.page_content}\n\nUser question: {state['question']}")
            ]
            
            # Get grade directly from LLM, but do not stream
            grading_llm = llm.bind(stream=False)
            response = await grading_llm.ainvoke(messages)
            try:
                score = float(response.content.strip())
                grades.append({"content": doc.page_content, "score": score})
                
                if score >= relevance_threshold:
                    filtered_docs.append(doc)
                else:
                    needs_web_search = True
            except ValueError:
                needs_web_search = True
                continue
        
        # Create single grading summary message
        grading_msg = AIMessage(
            content="",
            additional_kwargs={
                "action": {
                    "type": "grading",
                    "grades": grades,
                    "filtered_count": len(filtered_docs),
                    "needs_web_search": needs_web_search
                }
            }
        )
        
        return {
            **state,
            "documents": filtered_docs,
            "web_search_needed": needs_web_search,
            "messages": state["messages"] + [grading_msg]
        }

    async def transform_query(state: GraphState) -> GraphState:
        """Transform query using direct message invocation."""
        if not question_rewriter_prompt:
            return state
            
        # Create rewriting prompt messages
        messages = [
            SystemMessage(content=question_rewriter_prompt),
            HumanMessage(content=f"Question: {state['question']}\n\nRewrite this as a better search query:")
        ]
        
        # Get rewritten query directly from LLM
        rewriting_llm = llm.bind(stream=False)
        response = await rewriting_llm.ainvoke(messages)
        new_question = response.content.strip()
        
        # Create transform message
        transform_msg = AIMessage(
            content="",
            additional_kwargs={
                "action": {
                    "type": "query_transform",
                    "original_question": state["question"],
                    "transformed_question": new_question
                }
            }
        )
        
        return {
            **state,
            "question": new_question,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "messages": state["messages"] + [transform_msg]
        }

    async def perform_web_search(state: GraphState) -> GraphState:
        """Perform web search with proper message handling."""
        if not enable_web_search or not web_search_tool or not state.get("web_search_needed"):
            return state
            
        search_results = await web_search_tool.ainvoke({
            "query": state["question"]
        })
        
        web_docs = []
        for result in search_results:
            web_docs.append(Document(
                page_content=result["content"],
                metadata={
                    "source": result["url"],
                    "score": result.get("relevance_score", 1.0)
                }
            ))
        
        # Create web search message
        search_msg = AIMessage(
            content="",
            additional_kwargs={
                "action": {
                    "type": "web_search",
                    "results": [
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        }
                        for doc in web_docs
                    ]
                }
            }
        )
        
        docs = state["documents"]
        docs.extend(web_docs)
        return {
            **state,
            "documents": docs,
            "messages": state["messages"] + [search_msg]
        }

    async def generate(state: GraphState) -> GraphState:
        """Generate final answer using streaming chain."""
        context = "\n\n".join(doc.page_content for doc in state["documents"])
        generation = await generation_chain.ainvoke({
            "context": context,
            "question": state["question"]
        })
        
        # Final generation uses content field for streaming
        return {**state, "generation": generation}

    def decide_next_step(state: GraphState) -> str:
        """Determine next step in workflow."""
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= max_corrective_iterations:
            return "generate"
            
        if state.get("web_search_needed") and enable_web_search:
            return "transform_query"
            
        return "generate"

    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents) 
    workflow.add_node("generate", generate)
    
    if enable_web_search:
        workflow.add_node("transform_query", transform_query)
        workflow.add_node("perform_web_search", perform_web_search)
    
    # Add edges
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    
    workflow.add_conditional_edges(
        "grade_documents",
        decide_next_step,
        {
            "transform_query": "transform_query",
            "generate": "generate"
        }
    )
    
    if enable_web_search:
        workflow.add_edge("transform_query", "perform_web_search")
        workflow.add_edge("perform_web_search", "grade_documents")
    
    workflow.add_edge("generate", END)

    checkpoint = get_checkpointer()
    app = workflow.compile(checkpointer=checkpoint)
    return app