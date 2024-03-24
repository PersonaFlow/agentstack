from functools import lru_cache
import os
from langchain_openai import AzureChatOpenAI, ChatOpenAI


@lru_cache(maxsize=4)
def get_openai_llm(gpt_4: bool = False, azure: bool = False):
    if not azure:
        llm = ChatOpenAI(
            model='gpt-4-1106-preview' if gpt_4 else 'gpt-3.5-turbo-1106',
            temperature=0,
            streaming=True
        )
    else:
        llm = AzureChatOpenAI(
            temperature=0,
            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_base=os.environ["AZURE_OPENAI_API_BASE"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
            streaming=True,
        )
    return llm
