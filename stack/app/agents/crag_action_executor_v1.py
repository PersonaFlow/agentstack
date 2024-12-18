from typing import List, TypedDict, Sequence, Optional, Union, Dict, Any
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langgraph.graph import END, StateGraph, START
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from stack.app.core.datastore import get_checkpointer


class GraphState(TypedDict):
    """Represents the state of the CRAG graph."""

    question: str
    generation: str
    web_search_needed: bool
    documents: List[str]
    iteration_count: int
    actions: List[AIMessage]


def create_action_message(action_type: str, output: Any) -> AIMessage:
    """Create an AIMessage for a CRAG action."""
    return AIMessage(
        content="",
        additional_kwargs={"action": {"type": action_type, "output": output}},
    )


class ActionAwareChain:
    """Wrapper for LCEL chains to properly handle action messages."""

    def __init__(self, chain, action_type: str):
        self.chain = chain
        self.action_type = action_type

    async def ainvoke(self, input_data: Dict[str, Any]) -> AIMessage:
        result = await self.chain.ainvoke(input_data)
        return create_action_message(self.action_type, result)


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
    """Create a CRAG executor with action-aware message handling."""

    # Create grader chain
    grader_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert at evaluating document relevance.
            Rate the relevance of retrieved documents to the user's question on a scale of 0.0 to 1.0.
            - 1.0: Perfectly relevant, directly answers the question
            - 0.7: Highly relevant, contains most of the needed information
            - 0.5: Moderately relevant, contains some useful information
            - 0.3: Slightly relevant, touches on the topic but doesn't address the question
            - 0.0: Not relevant at all

            Return ONLY the numerical score without any explanation.""",
            ),
            ("human", "Retrieved document: {document}\n\nUser question: {question}"),
        ]
    )
    grader_base = grader_prompt | llm | StrOutputParser()
    relevance_grader = ActionAwareChain(grader_base, "grading")

    # Create rewriter chain if prompt provided
    question_rewriter = None
    if question_rewriter_prompt:
        rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", question_rewriter_prompt),
                (
                    "human",
                    "Question: {question}\n\nRewrite this as a better search query:",
                ),
            ]
        )
        rewrite_base = rewrite_prompt | llm | StrOutputParser()
        question_rewriter = ActionAwareChain(rewrite_base, "query_transform")

    # Create generation chain (remains normal since it's final output)
    rag_prompt = ChatPromptTemplate.from_template(
        "{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    rag_chain = rag_prompt | llm | StrOutputParser()

    async def retrieve(state: GraphState) -> GraphState:
        """Retrieve documents with action tracking."""
        docs = await retriever.aget_relevant_documents(state["question"])
        action_msg = create_action_message(
            "retrieval",
            [{"content": d.page_content, "metadata": d.metadata} for d in docs],
        )
        return {
            **state,
            "documents": docs,
            "actions": state.get("actions", []) + [action_msg],
        }

    async def grade_documents(state: GraphState) -> GraphState:
        """Grade documents with action tracking."""
        filtered_docs = []
        needs_web_search = False
        grades = []

        for doc in state["documents"]:
            try:
                grade_msg = await relevance_grader.ainvoke(
                    {"document": doc.page_content, "question": state["question"]}
                )
                score = float(grade_msg.additional_kwargs["action"]["output"].strip())
                grades.append({"content": doc.page_content, "score": score})

                if score >= relevance_threshold:
                    filtered_docs.append(doc)
                else:
                    needs_web_search = True
            except ValueError:
                needs_web_search = True
                continue

        action_msg = create_action_message("grading_summary", grades)
        return {
            **state,
            "documents": filtered_docs,
            "web_search_needed": needs_web_search,
            "actions": state.get("actions", []) + [action_msg],
        }

    async def transform_query(state: GraphState) -> GraphState:
        """Transform query with action tracking."""
        if not question_rewriter:
            return state

        action_msg = await question_rewriter.ainvoke({"question": state["question"]})
        new_question = action_msg.additional_kwargs["action"]["output"]

        return {
            **state,
            "question": new_question,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "actions": state.get("actions", []) + [action_msg],
        }

    async def perform_web_search(state: GraphState) -> GraphState:
        """Perform web search with action tracking."""
        if (
            not enable_web_search
            or not web_search_tool
            or not state.get("web_search_needed")
        ):
            return state

        search_results = await web_search_tool.ainvoke({"query": state["question"]})

        # Convert Tavily results to documents
        from langchain.schema import Document

        web_docs = []
        for result in search_results:
            web_docs.append(
                Document(
                    page_content=result["content"],
                    metadata={
                        "source": result["url"],
                        "score": result.get("relevance_score", 1.0),
                    },
                )
            )

        action_msg = create_action_message(
            "web_search",
            [{"content": d.page_content, "metadata": d.metadata} for d in web_docs],
        )

        docs = state["documents"]
        docs.extend(web_docs)
        return {
            **state,
            "documents": docs,
            "actions": state.get("actions", []) + [action_msg],
        }

    async def generate(state: GraphState) -> GraphState:
        """Generate final answer."""
        generation = await rag_chain.ainvoke(
            {
                "context": [d.page_content for d in state["documents"]],
                "question": state["question"],
            }
        )
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
        {"transform_query": "transform_query", "generate": "generate"},
    )

    if enable_web_search:
        workflow.add_edge("transform_query", "perform_web_search")
        workflow.add_edge("perform_web_search", "grade_documents")

    workflow.add_edge("generate", END)

    checkpoint = get_checkpointer()
    app = workflow.compile(checkpointer=checkpoint)
    return app
