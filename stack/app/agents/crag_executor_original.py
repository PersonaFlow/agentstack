from typing import List, TypedDict, Sequence, Optional, Union, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.prebuilt.tool_executor import ToolInvocation
from stack.app.core.datastore import get_checkpointer


class GraphState(TypedDict):
    """
    Represents the state of the CRAG graph.
    """
    question: str
    generation: str
    web_search_needed: bool  
    documents: List[str]
    iteration_count: int  

def get_crag_executor(
    llm: ChatOpenAI,
    retriever,
    system_prompt: str,
    web_search_tool=None,
    question_rewriter_prompt: Optional[str] = None,
    max_corrective_iterations: int = 3,
    enable_web_search: bool = True,
    relevance_threshold: float = 0.7,
):
    
    # Create the base chains
    rag_prompt = ChatPromptTemplate.from_template(
        "{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    rag_chain = rag_prompt | llm | StrOutputParser()
    
    # grader_prompt = ChatPromptTemplate.from_messages([
    #     ("system", system_prompt),
    #     ("human", "Retrieved document: {document}\n\nUser question: {question}")
    # ])

    grader_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at evaluating document relevance.
            Rate the relevance of retrieved documents to the user's question on a scale of 0.0 to 1.0.
            - 1.0: Perfectly relevant, directly answers the question
            - 0.7: Highly relevant, contains most of the needed information
            - 0.5: Moderately relevant, contains some useful information
            - 0.3: Slightly relevant, touches on the topic but doesn't address the question
            - 0.0: Not relevant at all

            Return ONLY the numerical score without any explanation."""),
        ("human", "Retrieved document: {document}\n\nUser question: {question}")
    ])
    
    relevance_grader = grader_prompt | llm | StrOutputParser()

    if question_rewriter_prompt:
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", question_rewriter_prompt),
            ("human", "Question: {question}\n\nRewrite this as a better search query:")
        ])
        question_rewriter = rewrite_prompt | llm | StrOutputParser()
    
    async def retrieve(state: GraphState) -> GraphState:
        """Retrieve documents."""
        docs = await retriever.aget_relevant_documents(state["question"])
        return {
            **state,
            "documents": docs,
        }
    
    async def generate(state: GraphState) -> GraphState:
        """Generate answer."""
        generation = await rag_chain.ainvoke({
            "context": state["documents"],
            "question": state["question"]
        })
        return {**state, "generation": generation}
    
    async def grade_documents(state: GraphState) -> GraphState:
        """Grade document relevance."""
        filtered_docs = []
        needs_web_search = False
        
        for doc in state["documents"]:
            try:
                # Get relevance score and ensure it's a float
                score_str = await relevance_grader.ainvoke({
                    "document": doc.page_content,
                    "question": state["question"]
                })
                score = float(score_str.strip())
                
                if score >= relevance_threshold:
                    filtered_docs.append(doc)
                else:
                    needs_web_search = True
            except ValueError as e:
                # logger.warning(f"Invalid score returned by grader: {score_str}. Using 0.0")
                needs_web_search = True
                continue
                
        return {
            **state,
            "documents": filtered_docs,
            "web_search_needed": needs_web_search
        }
    
    async def transform_query(state: GraphState) -> GraphState:
        """Transform query if needed."""
        if not question_rewriter_prompt:
            return state
            
        new_question = await question_rewriter.ainvoke({
            "question": state["question"]
        })
        return {
            **state, 
            "question": new_question,
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    async def perform_web_search(state: GraphState) -> GraphState:  
        """Perform web search if enabled."""
        if not enable_web_search or not web_search_tool or not state.get("web_search_needed"):
            return state
            
        search_results = await web_search_tool.ainvoke({
            "query": state["question"]
        })
        
        # Convert Tavily results to documents
        from langchain.schema import Document
        web_docs = []
        for result in search_results:
            web_docs.append(Document(
                page_content=result["content"],
                metadata={
                    "source": result["url"],
                    "score": result.get("relevance_score", 1.0)
                }
            ))
            
        docs = state["documents"]
        docs.extend(web_docs)
        return {**state, "documents": docs}
    
    def decide_next_step(state: GraphState) -> str:
        """Determine next step in workflow."""
        # Check if we've hit max iterations
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
    
    # config: Dict[str, Any] = {
    #     "recursion_limit": max_corrective_iterations + 1  # Add 1 to account for initial run
    # }
    checkpoint = get_checkpointer()
    app = workflow.compile(checkpointer=checkpoint)
    
    # Bind the config
    return app

