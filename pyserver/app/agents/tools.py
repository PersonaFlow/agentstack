from functools import lru_cache
from enum import Enum

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain_community.retrievers import (
    PubMedRetriever,
    WikipediaRetriever,
)
from langchain_community.retrievers.you import YouRetriever
from langchain_community.tools import ArxivQueryRun, DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilyAnswer, TavilySearchResults
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient
from app.core.configuration import get_settings
from langchain_openai import OpenAIEmbeddings
# from langchain_robocorp import ActionServerToolkit

settings = get_settings()
class DDGInput(BaseModel):
    query: str = Field(description="search query to look up")


class ArxivInput(BaseModel):
    query: str = Field(description="search query to look up")


class PythonREPLInput(BaseModel):
    query: str = Field(description="python command to run")


RETRIEVAL_DESCRIPTION = """Can be used to look up information that was uploaded for this assistant.
If the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!"""


def get_retriever(assistant_id: str):
    qdrant = Qdrant(
            client = QdrantClient("localhost", port=6333),
            collection_name = assistant_id,
            embeddings = OpenAIEmbeddings(),
            vector_name = assistant_id
        )
    return qdrant.as_retriever()

@lru_cache(maxsize=5)
def get_retrieval_tool(assistant_id: str, description: str):
    return create_retriever_tool(
        get_retriever(assistant_id),
        "Retriever",
        description,
    )


@lru_cache(maxsize=1)
def _get_duck_duck_go():
    return DuckDuckGoSearchRun(args_schema=DDGInput)


@lru_cache(maxsize=1)
def _get_arxiv():
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(), args_schema=ArxivInput)


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


if settings.TAVILY_API_KEY:
    @lru_cache(maxsize=1)
    def _get_tavily():
        tavily_search = TavilySearchAPIWrapper()
        return TavilySearchResults(api_wrapper=tavily_search)

    @lru_cache(maxsize=1)
    def _get_tavily_answer():
        tavily_search = TavilySearchAPIWrapper()
        return TavilyAnswer(api_wrapper=tavily_search)

# TODO: Include RoboCorp Action Server
# @lru_cache(maxsize=1)
# def _get_action_server():
#     toolkit = ActionServerToolkit(
#         url=os.environ.get("ROBOCORP_ACTION_SERVER_URL"),
#         api_key=os.environ.get("ROBOCORP_ACTION_SERVER_KEY"),
#     )
#     tools = toolkit.get_tools()
#     return tools


class AvailableTools(str, Enum):
    # ACTION_SERVER = "Action Server by Robocorp"
    DDG_SEARCH = "DDG Search"
    TAVILY = "Search (Tavily)" if settings.TAVILY_API_KEY else None
    TAVILY_ANSWER = "Search (short answer, Tavily)" if settings.TAVILY_API_KEY else None
    RETRIEVAL = "Retrieval"
    ARXIV = "Arxiv"
    PUBMED = "PubMed"
    WIKIPEDIA = "Wikipedia"


TOOLS = {
    # AvailableTools.ACTION_SERVER: _get_action_server,
    AvailableTools.DDG_SEARCH: _get_duck_duck_go,
    AvailableTools.ARXIV: _get_arxiv,
    AvailableTools.PUBMED: _get_pubmed,
    AvailableTools.WIKIPEDIA: _get_wikipedia,
}

if settings.TAVILY_API_KEY:
    TOOLS[AvailableTools.TAVILY_ANSWER] = _get_tavily_answer
    TOOLS[AvailableTools.TAVILY] = _get_tavily

TOOL_OPTIONS = {e.value: e.value for e in AvailableTools}

# Check if dependencies and env vars for each tool are available
for k, v in TOOLS.items():
    v()
