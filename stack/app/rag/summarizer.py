from typing import Optional
from stack.app.core.configuration import get_settings
from stack.app.schema.rag import BaseDocumentChunk
from stack.app.agents.llm import (
    get_openai_llm,
    get_anthropic_llm,
    get_google_llm,
    get_mixtral_fireworks,
    get_ollama_llm,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


SUMMARY_SUFFIX = "summary"
settings = get_settings()


class Summarizer:
    def __init__(self):
        self.llm = self._get_llm()
        self.prompt = ChatPromptTemplate.from_template(
            "Make an in-depth summary of the block of text below:\n\n"
            "Text:\n"
            "------------------------------------------\n"
            "{text}\n"
            "------------------------------------------\n\n"
            "Your summary:"
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _get_llm(self) -> BaseChatModel:
        provider = settings.SUMMARIZATION_MODEL_PROVIDER.lower()
        model_name = settings.SUMMARIZATION_MODEL_NAME

        if provider == "openai":
            return get_openai_llm(model=model_name)
        elif provider == "anthropic":
            return get_anthropic_llm()
        elif provider == "google":
            return get_google_llm()
        elif provider == "mixtral":
            return get_mixtral_fireworks()
        elif provider == "ollama":
            return get_ollama_llm()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def summarize(self, document: BaseDocumentChunk) -> str:
        return await self.chain.ainvoke({"text": document.page_content})


async def completion(*, document: BaseDocumentChunk) -> str:
    summarizer = Summarizer()
    return await summarizer.summarize(document)
