from enum import Enum
import logging
from functools import lru_cache
from urllib.parse import urlparse
import boto3
import httpx
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import BedrockChat, ChatFireworks
from langchain_community.chat_models.ollama import ChatOllama
from langchain_google_vertexai import ChatVertexAI
from stack.app.core.configuration import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class BotType(str, Enum):
    chatbot = "chatbot"
    chat_retrieval = "chat_retrieval"
    agent = "agent"
    corrective_rag = "corrective_rag"


class AgentType(str, Enum):
    GPT_4O_MINI = "GPT 4o Mini"
    GPT_4 = "GPT 4 Turbo"
    GPT_4O = "GPT 4o"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"
    ANTHROPIC_CLAUDE = "Anthropic Claude"
    BEDROCK_ANTHROPIC_CLAUDE = "Anthropic Claude (Amazon Bedrock)"
    GEMINI = "GEMINI"
    OLLAMA = "Ollama"


class LLMType(str, Enum):
    GPT_4O_MINI = "GPT 4o Mini"
    GPT_4 = "GPT 4"
    GPT_4O = "GPT 4o"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"
    ANTHROPIC_CLAUDE = "Anthropic Claude"
    BEDROCK_ANTHROPIC_CLAUDE = "Anthropic Claude (Amazon Bedrock)"
    GEMINI = "GEMINI"
    OLLAMA = "Ollama"


def get_llm(llm_type: LLMType):
    if llm_type == LLMType.GPT_4O_MINI:
        llm = get_openai_llm()
    elif llm_type == LLMType.GPT_4:
        llm = get_openai_llm(model="gpt-4-turbo")
    elif llm_type == LLMType.GPT_4O:
        llm = get_openai_llm(model="gpt-4o")
    elif llm_type == LLMType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
    elif llm_type == LLMType.ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm()
    elif llm_type == LLMType.BEDROCK_ANTHROPIC_CLAUDE:
        llm = get_anthropic_llm(bedrock=True)
    elif llm_type == LLMType.GEMINI:
        llm = get_google_llm()
    elif llm_type == LLMType.OLLAMA:
        llm = get_ollama_llm()
    else:
        raise ValueError(f"Unexpected llm type: {llm_type}")
    return llm


@lru_cache(maxsize=4)
def get_openai_llm(model: str = "gpt-4o-mini", azure: bool = False):
    proxy_url = settings.OPENAI_PROXY_URL
    http_client = None
    if proxy_url:
        parsed_url = urlparse(proxy_url)
        if parsed_url.scheme and parsed_url.netloc:
            http_client = httpx.AsyncClient(proxies=proxy_url)
        else:
            logger.warn("Invalid proxy URL provided. Proceeding without proxy.")

    if not azure:
        try:
            llm = ChatOpenAI(
                model=model,
                http_client=http_client,
                temperature=0,
            )
            return llm
        except Exception as e:
            logger.error(f"Failed to instantiate ChatOpenAI due to: {str(e)}.")
    else:
        llm = AzureChatOpenAI(
            temperature=0,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_base=settings.AZURE_OPENAI_API_BASE,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
        )  # type: ignore
        return llm


@lru_cache(maxsize=2)
def get_anthropic_llm(bedrock: bool = False):
    if bedrock:
        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_BEDROCK_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        model = BedrockChat(model_id=settings.AWS_BEDROCK_CHAT_MODEL_ID, client=client)
    else:
        model = ChatAnthropic(
            model_name=settings.ANTHROPIC_MODEL_NAME,
            max_tokens_to_sample=2000,
            temperature=0,
        )  # type: ignore
    return model


@lru_cache(maxsize=1)
def get_google_llm():
    return ChatVertexAI(
        model_name=settings.GOOGLE_VERTEX_MODEL,
        convert_system_message_to_human=True,
        streaming=True,
    )


@lru_cache(maxsize=1)
def get_mixtral_fireworks():
    return ChatFireworks(model=settings.MIXTRAL_FIREWORKS_MODEL_NAME)


@lru_cache(maxsize=1)
def get_ollama_llm():
    model_name = settings.OLLAMA_MODEL
    ollama_base_url = settings.OLLAMA_BASE_URL
    return ChatOllama(model=model_name, base_url=ollama_base_url)
