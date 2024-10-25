from enum import Enum
from functools import lru_cache
from typing import Optional, Any
import structlog
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits.connery import ConneryToolkit
from langchain_community.retrievers.kay import KayAiRetriever
from langchain_community.retrievers.pubmed import PubMedRetriever
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from langchain_community.retrievers.you import YouRetriever
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.connery import ConneryService
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import (
    TavilyAnswer as _TavilyAnswer,
)
from langchain_community.tools.tavily_search import (
    TavilySearchResults,
)
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import Tool
from langchain_robocorp import ActionServerToolkit
from typing_extensions import TypedDict, NotRequired
from stack.app.rag.custom_retriever import Retriever
from stack.app.core.configuration import settings
from stack.app.schema.rag import VectorDatabase, EncoderConfig


class DDGInput(BaseModel):
    query: str = Field(description="search query to look up")


class ArxivInput(BaseModel):
    query: str = Field(description="search query to look up")


class PythonREPLInput(BaseModel):
    query: str = Field(description="python command to run")


class DallEInput(BaseModel):
    query: str = Field(description="image description to generate image from")


class AvailableTools(str, Enum):
    ACTION_SERVER = "action_server_by_robocorp"
    CONNERY = "ai_action_runner_by_connery"
    DDG_SEARCH = "ddg_search"
    TAVILY = "search_tavily"
    TAVILY_ANSWER = "search_tavily_answer"
    RETRIEVAL = "retrieval"
    ARXIV = "arxiv"
    YOU_SEARCH = "you_search"
    SEC_FILINGS = "sec_filings_kai_ai"
    PRESS_RELEASES = "press_releases_kai_ai"
    PUBMED = "pubmed"
    WIKIPEDIA = "wikipedia"
    DALL_E = "dall_e"


class ToolConfig(TypedDict):
    ...


class BaseTool(BaseModel):
    type: AvailableTools = Field(
        title="Tool Type",
        description="The type of tool as defined by the AvailableTools enum.",
    )
    description: Optional[str] = Field(
        title="Tool Description", description="A brief description of the tool."
    )
    name: Optional[str] = Field(
        title="Tool Name",
        description="The name of the tool.",
    )
    config: Optional[ToolConfig] = Field(
        title="Tool Configuration",
        description="A field for additional configuration of the tool.",
    )
    multi_use: Optional[bool] = Field(
        default=False,
        title="Multi-Use",
        description="Whether or not this is a multi-use tool.",
    )


class RetrievalConfigDict(ToolConfig):
    index_name: NotRequired[str]
    encoder: NotRequired[dict]
    vector_database: NotRequired[dict]
    enable_rerank: NotRequired[bool]


# Pydantic model for validation of the retrieval config
class RetrievalConfigModel(BaseModel):
    index_name: Optional[str] = Field(
        default=settings.VECTOR_DB_COLLECTION_NAME,
        description="Name of the vector database collection to query from",
    )
    encoder: Optional[EncoderConfig] = Field(
        default_factory=EncoderConfig, description="Embeddings provider configuration"
    )
    vector_database: Optional[VectorDatabase] = Field(
        default_factory=VectorDatabase, description="Vector database configuration"
    )
    enable_rerank: Optional[bool] = Field(
        default=settings.ENABLE_RERANK_BY_DEFAULT,
        description="Enable reranking of results",
    )

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> RetrievalConfigDict:
        return {
            "index_name": self.index_name,
            "encoder": self.encoder.model_dump() if self.encoder else None,
            "vector_database": self.vector_database.model_dump()
            if self.vector_database
            else None,
            "enable_rerank": self.enable_rerank,
        }


class RetrievalConfig(ToolConfig, RetrievalConfigDict):
    pass


class Retrieval(BaseTool):
    type: AvailableTools = Field(AvailableTools.RETRIEVAL, const=True)
    name: str = Field("Retrieval", const=True)
    description: str = Field("Look up information in uploaded files.", const=True)
    config: RetrievalConfig = Field(
        default_factory=lambda: RetrievalConfigModel().to_dict()
    )


class ActionServerConfig(ToolConfig):
    url: str
    api_key: str


class ActionServer(BaseTool):
    type: AvailableTools = Field(AvailableTools.ACTION_SERVER, const=True)
    name: str = Field("Action Server by Sem4.ai", const=True)
    description: str = Field(
        (
            "Run AI actions with "
            "[Sema4.ai Action Server](https://github.com/Sema4AI/actions)."
        ),
        const=True,
    )
    config: ActionServerConfig
    multi_use: bool = Field(True, const=True)


class Connery(BaseTool):
    type: AvailableTools = Field(AvailableTools.CONNERY, const=True)
    name: str = Field("AI Action Runner by Connery", const=True)
    description: str = Field(
        (
            "Connect OpenGPTs to the real world with "
            "[Connery](https://github.com/connery-io/connery)."
        ),
        const=True,
    )


class DDGSearch(BaseTool):
    type: AvailableTools = Field(AvailableTools.DDG_SEARCH, const=True)
    name: str = Field("DuckDuckGo Search", const=True)
    description: str = Field(
        "Search the web with [DuckDuckGo](https://pypi.org/project/duckduckgo-search/).",
        const=True,
    )


class Arxiv(BaseTool):
    type: AvailableTools = Field(AvailableTools.ARXIV, const=True)
    name: str = Field("Arxiv", const=True)
    description: str = Field("Searches [Arxiv](https://arxiv.org/).", const=True)


class YouSearch(BaseTool):
    type: AvailableTools = Field(AvailableTools.YOU_SEARCH, const=True)
    name: str = Field("You.com Search", const=True)
    description: str = Field(
        "Uses [You.com](https://you.com/) search, optimized responses for LLMs.",
        const=True,
    )


class SecFilings(BaseTool):
    type: AvailableTools = Field(AvailableTools.SEC_FILINGS, const=True)
    name: str = Field("SEC Filings (Kay.ai)", const=True)
    description: str = Field(
        "Searches through SEC filings using [Kay.ai](https://www.kay.ai/).", const=True
    )


class PressReleases(BaseTool):
    type: AvailableTools = Field(AvailableTools.PRESS_RELEASES, const=True)
    name: str = Field("Press Releases (Kay.ai)", const=True)
    description: str = Field(
        "Searches through press releases using [Kay.ai](https://www.kay.ai/).",
        const=True,
    )


class PubMed(BaseTool):
    type: AvailableTools = Field(AvailableTools.PUBMED, const=True)
    name: str = Field("PubMed", const=True)
    description: str = Field(
        "Searches [PubMed](https://pubmed.ncbi.nlm.nih.gov/).", const=True
    )


class Wikipedia(BaseTool):
    type: AvailableTools = Field(AvailableTools.WIKIPEDIA, const=True)
    name: str = Field("Wikipedia", const=True)
    description: str = Field(
        "Searches [Wikipedia](https://pypi.org/project/wikipedia/).", const=True
    )


class Tavily(BaseTool):
    type: AvailableTools = Field(AvailableTools.TAVILY, const=True)
    name: str = Field("Search (Tavily)", const=True)
    description: str = Field(
        (
            "Uses the [Tavily](https://app.tavily.com/) search engine. "
            "Includes sources in the response."
        ),
        const=True,
    )


class TavilyAnswer(BaseTool):
    type: AvailableTools = Field(AvailableTools.TAVILY_ANSWER, const=True)
    name: str = Field("Search (short answer, Tavily)", const=True)
    description: str = Field(
        (
            "Uses the [Tavily](https://app.tavily.com/) search engine. "
            "This returns only the answer, no supporting evidence."
        ),
        const=True,
    )


class DallE(BaseTool):
    type: AvailableTools = Field(AvailableTools.DALL_E, const=True)
    name: str = Field("Generate Image (Dall-E)", const=True)
    description: str = Field(
        "Generates images from a text description using OpenAI's DALL-E model.",
        const=True,
    )


RETRIEVAL_DESCRIPTION = """Can be used to look up information that was uploaded to this assistant.
If the user is referencing particular files, that is often a good hint that information may be here.
If the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!"""


def get_retriever(
    assistant_id: str, thread_id: str, config: Optional[dict] = None
) -> Retriever:
    logger = structlog.get_logger()
    if not assistant_id or not thread_id:
        return

    namespace = assistant_id if assistant_id is not None else thread_id
    metadata: dict = {"namespace": namespace}

    # Always include defaults
    metadata["vector_database"] = VectorDatabase().model_dump()
    metadata["encoder"] = EncoderConfig().model_dump()
    metadata["enable_rerank"] = settings.ENABLE_RERANK_BY_DEFAULT
    metadata["index_name"] = settings.VECTOR_DB_COLLECTION_NAME

    if config:
        logger.debug("Retriever config", config=config)
        metadata.update({k: v for k, v in config.items() if v is not None})

        if metadata.get("encoder"):
            # Need to convert dict to EncoderConfig for validation then back to dict
            encoder_config = EncoderConfig(**metadata["encoder"])
            metadata["encoder"] = encoder_config.model_dump()

        if metadata.get("vector_database"):
            vector_db_config = VectorDatabase(**metadata["vector_database"])
            metadata["vector_database"] = vector_db_config.model_dump()

    return Retriever(metadata=metadata)


def get_retrieval_tool(
    assistant_id: str, thread_id: str, description: str, config: RetrievalConfig
):
    retriever = get_retriever(
        assistant_id=assistant_id, thread_id=thread_id, config=config
    )
    return create_retriever_tool(
        retriever,
        "Retrieval",
        description,
    )


@lru_cache(maxsize=1)
def _get_duck_duck_go():
    return DuckDuckGoSearchRun(args_schema=DDGInput)


@lru_cache(maxsize=1)
def _get_arxiv():
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(), args_schema=ArxivInput)


@lru_cache(maxsize=1)
def _get_you_search():
    return create_retriever_tool(
        YouRetriever(n_hits=3, n_snippets_per_hit=3),
        "you_search",
        "Searches for documents using You.com",
    )


@lru_cache(maxsize=1)
def _get_sec_filings():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["10-K", "10-Q"], num_contexts=3
        ),
        "sec_filings_search",
        "Search for a query among SEC Filings",
    )


@lru_cache(maxsize=1)
def _get_press_releases():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["PressRelease"], num_contexts=6
        ),
        "press_release_search",
        "Search for a query among press releases from US companies",
    )


@lru_cache(maxsize=1)
def _get_pubmed():
    return create_retriever_tool(
        PubMedRetriever(), "pub_med_search", "Search for a query on PubMed"
    )


@lru_cache(maxsize=1)
def _get_wikipedia():
    return create_retriever_tool(
        WikipediaRetriever(), "wikipedia", "Search for a query on Wikipedia"
    )


@lru_cache(maxsize=1)
def _get_tavily():
    tavily_search = TavilySearchAPIWrapper()
    return TavilySearchResults(api_wrapper=tavily_search, name="search_tavily")


@lru_cache(maxsize=1)
def _get_tavily_answer():
    tavily_search = TavilySearchAPIWrapper()
    return _TavilyAnswer(api_wrapper=tavily_search, name="search_tavily_answer")


def _get_action_server(**kwargs: ActionServerConfig):
    toolkit = ActionServerToolkit(url=kwargs["url"], api_key=kwargs["api_key"])
    tools = toolkit.get_tools()
    return tools


@lru_cache(maxsize=1)
def _get_connery_actions():
    connery_service = ConneryService()
    connery_toolkit = ConneryToolkit.create_instance(connery_service)
    tools = connery_toolkit.get_tools()
    return tools


@lru_cache(maxsize=1)
def _get_dalle_tools():
    return Tool(
        "Dall-E-Image-Generator",
        DallEAPIWrapper(size="1024x1024", quality="hd").run,
        "A wrapper around OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description.",
    )


TOOLS = {
    AvailableTools.ACTION_SERVER: _get_action_server,
    AvailableTools.CONNERY: _get_connery_actions,
    AvailableTools.DDG_SEARCH: _get_duck_duck_go,
    AvailableTools.ARXIV: _get_arxiv,
    AvailableTools.YOU_SEARCH: _get_you_search,
    AvailableTools.SEC_FILINGS: _get_sec_filings,
    AvailableTools.PRESS_RELEASES: _get_press_releases,
    AvailableTools.PUBMED: _get_pubmed,
    AvailableTools.TAVILY: _get_tavily,
    AvailableTools.WIKIPEDIA: _get_wikipedia,
    AvailableTools.TAVILY_ANSWER: _get_tavily_answer,
    AvailableTools.DALL_E: _get_dalle_tools,
}
