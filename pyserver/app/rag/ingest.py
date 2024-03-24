from langchain.text_splitter import TextSplitter
from langchain_community.document_loaders import Blob
from langchain_community.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore


def _update_document_metadata(document: Document, assistant_id: str) -> None:
    """Mutation in place that adds a assistant_id to the document metadata."""
    document.metadata["assistant_id"] = assistant_id


def ingest_blob(
    blob: Blob,
    parser: BaseBlobParser,
    text_splitter: TextSplitter,
    vectorstore: VectorStore,
    assistant_id: str,
    *,
    batch_size: int = 100,
) -> list[str]:
    """Ingest a document into the vectorstore.
    Code is responsible for taking binary data, parsing it and then indexing it
    into a vector store.

    This code should be agnostic to how the blob got generated; i.e., it does not
    know about server/uploading etc.
    """
    docs_to_index = []
    ids = []
    for document in parser.lazy_parse(blob):
        docs = text_splitter.split_documents([document])
        for doc in docs:
            _update_document_metadata(doc, assistant_id)
        docs_to_index.extend(docs)

        if len(docs_to_index) >= batch_size:
            ids.extend(vectorstore.add_documents(docs_to_index))
            docs_to_index = []

    if docs_to_index:
        ids.extend(vectorstore.add_documents(docs_to_index))

    return ids
