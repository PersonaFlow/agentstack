from openai import AsyncOpenAI

from pyserver.app.schema.rag import BaseDocumentChunk
from pyserver.app.core.configuration import get_settings

SUMMARY_SUFFIX = "summary"
settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
)


def _generate_content(*, document: BaseDocumentChunk) -> str:
    return f"""Make an in depth summary the block of text below.

Text:
------------------------------------------
{document.page_content}
------------------------------------------

Your summary:"""


# TODO: Make this configurable
async def completion(*, document: BaseDocumentChunk) -> str:
    content = _generate_content(document=document)
    completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="gpt-3.5-turbo-16k",
    )

    return completion.choices[0].message.content or ""
