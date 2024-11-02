# corrective_rag_agent.py

from typing import List, Dict, Any, Optional, Sequence
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableBinding, ConfigurableField, RunnablePassthrough
from langchain.schema import Document, BaseMessage
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from stack.app.rag.custom_retriever import Retriever
from tools import Tavily
from configurable_agent import AgentType, get_llm, DEFAULT_SYSTEM_MESSAGE, RETRIEVAL_DESCRIPTION
from langgraph.graph.message import Messages
import langchain
from stack.app.agents.configurable_agent import chatbot, chat_retrieval

class GraphState(TypedDict):
    """
    Represents the state of our CRAG process.

    Attributes:
        messages: The current conversation messages
        documents: List of retrieved documents
        generation: LLM generation
        web_search: Whether to add search results
    """
    messages: Messages
    documents: List[Document]
    generation: Optional[str]
    web_search: str

class ConfigurableCorrectiveRagAgent(RunnableBinding):
    """
    A configurable agent that implements the Corrective RAG (CRAG) technique.
    """

    agent: AgentType
    system_message: str
    retrieval_description: str
    assistant_id: Optional[str]
    thread_id: Optional[str]
    crag_relevance_threshold: float = 0.7
    max_corrective_iterations: int = 3

    def __init__(
        self,
        agent: AgentType = AgentType.GPT_4O_MINI,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        retrieval_description: str = RETRIEVAL_DESCRIPTION,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        crag_relevance_threshold: float = 0.7,
        max_corrective_iterations: int = 3,
        **kwargs: Any
    ):
        self.agent = agent
        self.system_message = system_message
        self.retrieval_description = retrieval_description
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.crag_relevance_threshold = crag_relevance_threshold
        self.max_corrective_iterations = max_corrective_iterations

        self.llm = get_llm(agent)
        self.retriever = Retriever(metadata={"namespace": assistant_id or thread_id})
        self.web_search_tool = Tavily()

        workflow = self._build_graph()
        super().__init__(bound=workflow.compile(), kwargs=kwargs)

    def retrieve(self, state: GraphState) -> Dict[str, Any]:
        """Retrieve relevant documents."""
        question = state["messages"][-1].content if state["messages"] else ""
        documents = self.retriever.get_relevant_documents(question)
        return {"documents": documents, "messages": state["messages"]}

    def grade_documents(self, state: GraphState) -> Dict[str, Any]:
        """Grade the relevance of retrieved documents."""
        question = state["messages"][-1].content if state["messages"] else ""
        documents = state["documents"]

        grade_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a document grader assessing relevance to a question."),
            ("human", "Question: {question}\n\nDocument: {document}\n\nIs this document relevant?")
        ])
        grader_chain = grade_prompt | self.llm | StrOutputParser()

        filtered_docs = []
        web_search = "No"
        for doc in documents:
            grade = grader_chain.invoke({"question": question, "document": doc.page_content})
            if "yes" in grade.lower():
                filtered_docs.append(doc)
            else:
                web_search = "Yes"

        return {
            "documents": filtered_docs,
            "messages": state["messages"],
            "web_search": web_search
        }

    def generate(self, state: GraphState) -> Dict[str, Any]:
        """Generate a response based on the retrieved documents."""
        question = state["messages"][-1].content if state["messages"] else ""
        documents = state["documents"]

        prompt = langchain.hub.pull("rlm/rag-prompt")

        rag_chain = (
            {"context": lambda x: x["documents"], "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        generation = rag_chain.invoke({"documents": documents, "question": question})
        return {
            "documents": documents,
            "messages": state["messages"],
            "generation": generation
        }

    def transform_query(self, state: GraphState) -> Dict[str, Any]:
        """Transform the query for better web search results."""
        question = state["messages"][-1].content if state["messages"] else ""

        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a question rewriter that optimizes queries for web search."),
            ("human", "Original question: {question}\n\nRewrite this for optimal web search:")
        ])
        rewrite_chain = rewrite_prompt | self.llm | StrOutputParser()

        new_question = rewrite_chain.invoke({"question": question})
        return {
            "documents": state["documents"],
            "messages": state["messages"][:-1] + [BaseMessage(content=new_question)],
        }

    def web_search(self, state: GraphState) -> Dict[str, Any]:
        """Perform a web search to supplement retrieved documents."""
        question = state["messages"][-1].content if state["messages"] else ""
        documents = state["documents"]

        search_results = self.web_search_tool.invoke({"query": question})
        web_results = Document(page_content="\n".join([d["content"] for d in search_results]))
        documents.append(web_results)

        return {
            "documents": documents,
            "messages": state["messages"],
        }

    def decide_to_generate(self, state: GraphState) -> str:
        """Decide whether to generate an answer or transform the query."""
        web_search = state.get("web_search", "No")
        return "transform_query" if web_search == "Yes" else "generate"

    def _build_graph(self) -> StateGraph:
        """Build the CRAG process graph."""
        workflow = StateGraph(GraphState)

        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)
        workflow.add_node("transform_query", self.transform_query)
        workflow.add_node("web_search", self.web_search)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "web_search")
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("generate", "end")

        return workflow

# The configuration for corrective_rag should be added to configurable_agent.py
corrective_rag = (
    ConfigurableCorrectiveRagAgent(
        agent=AgentType.GPT_4O_MINI,
        system_message=DEFAULT_SYSTEM_MESSAGE,
        retrieval_description=RETRIEVAL_DESCRIPTION,
        assistant_id=None,
        thread_id=None,
    )
    .configurable_fields(
        agent=ConfigurableField(id="agent_type", name="Agent Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        crag_relevance_threshold=ConfigurableField(id="relevance_threshold", name="Relevance Threshold"),
        max_corrective_iterations=ConfigurableField(id="max_iterations", name="Max Iterations"),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
        thread_id=ConfigurableField(id="thread_id", name="Thread ID", is_shared=True),
        retrieval_description=ConfigurableField(
            id="retrieval_description", name="Retrieval Description"
        ),
    )
    .configurable_alternatives(
        ConfigurableField(id="type", name="Bot Type"),
        default_key="corrective_rag",
        prefix_keys=True,
        chatbot=chatbot,
        chat_retrieval=chat_retrieval,
    )
    .with_types(
        input_type=Messages,
        output_type=Sequence[AnyMessage],
    )
)