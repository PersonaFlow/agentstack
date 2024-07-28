# Re-export embedding providers from LangChain Community for maximum compatibility.
# Source - LangChain
# URL: https://github.com/langchain-ai/langchain/blob/6a5b084704afa22ca02f78d0464f35aed75d1ff2/libs/langchain/langchain_community/embeddings

from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.azure_openai import AzureOpenAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

__all__ = [
    "OllamaEmbeddings",
    "OpenAIEmbeddings",
    "HuggingFaceEmbeddings",
    "AzureOpenAIEmbeddings",
    "FastEmbedEmbeddings",
]
