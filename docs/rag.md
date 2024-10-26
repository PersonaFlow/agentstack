# Document Processing and RAG

AgentStack's document processing system can be used as part of the Assistants flow or as a standalone system for processing and querying structured or unstructured data. The system is designed to be modular and can be easily extended to support other embedding models and vector databases.

Processing of data is handled primarily by the embedding service, which orchestrates the partioning, chunking, embedding, and upserting of documents. The splitting of documents can be done by title, where title elements in the document are identified and used as split points, or splits can be created according to semantic similarity of the surrounding content. Splits can also be made using the standard recursive method with a chunk overlap.

>Semantic document processing is handled by [Unstructured](https://unstructured.io/) via our pre-processing ETL pipeline. The unstructured API docker image is included in the docker-compose.yml for this reason and is required to use the semantic splitting method.

The primary means of ingestion is via the `/rag/ingest` API. This endpoint provides a multitude of configuration options. The /assistants api also contains a convenience endpoint at `/api/v1/assistants/{assistant_id}/files` which simply takes the id of a file that has been uploaded, runs it through the ingestion pipeline, and adds it to the assistant's namespace in the vector store.


The `/api/v1/rag/ingest` and `/api/v1/rag/query` exist as standalone endpoints for document processing. 

The `/api/v1/rag/ingest` endpoint takes an array of file IDs. An optional webhook url can be provided, which is then called when all of the documents are processed. 


**/rag/ingest Example Request**:

```json
{
  "files": ["caafc6e4-fe4c-4de9-8c6f-10dd943c882e", "caafc6e4-fe4c-4de9-8c6f-10dd943c882e"],
  "purpose": "assistants",
  "namespace": "398067bf-4d89-4141-86f5-a795b063190b",
  "document_processor": {
    "summarize": true,
    "encoder": {
      "provider": "openai",
      "encoder_model": "text-embedding-3-small",
      "dimensions": 1536
    },
    "unstructured": {
      "partition_strategy": "auto",
      "hi_res_model_name": "detectron2_onnx",
      "process_tables": false
    },
    "splitter": {
      "name": "semantic",
      "min_tokens": 30,
      "max_tokens": 800,
      "rolling_window_size": 1,
      "prefix_titles": true,
      "prefix_summary": true
    }
  },
  "webhook_url": "http://my-domain.com/webhook"
}
```

**Notes**
- All `document_processor` fields are optional. If omitted, the system will use default values. The default values are also overridden by env variables.
- Use the /rag/ingest endpoint for ingesting documents during a conversation/thread, using the thread id for the namespace. 
- To use the documents with an assistant, set `purpose` to "assistants" and use the assistant id for the `namespace` parameter.
- `summarize`: If true, the system will generate summaries where appropriate that are ingested into a separate summary collection. This allows for summarization queries to be made which take the full context of the document into account. 
- `webhook_url`: This is an optional webhook that will be called when the ingestion has completed.
- `splitter.name`: Available options are `semantic`, `by_title`, and `recursive`. The `semantic` splitter uses the unstructured API to split documents based on semantic similarity. The `by_title` splitter uses the title elements in the document as split points. The `recursive` splitter uses a recursive method with a chunk overlap.
- There is currently a limitation where html pages have to end with the .html suffix to be processed. This will be mitigated in an upcoming release.
- For use-cases that involve multiple collections across different vector stores, the `vector_database` and `index_name` fields can be used to specifiy the location where the embeddings should be stored. This applies to both the ingest and query endpoints.

```json
(...)
  "vector_database": {
    "type": "qdrant",
    "config": {
      "host": "http://localhost:6333",
      "api_key": "123456789"
    }
  },
  "index_name": "custom"
(...)
```

## Assistant Retrieval
To use retrieval augmented generation (RAG) via an assistant, you can create an assistant using one of the architectures that support it. The `chat_retrieval` architecture has knowledge base retrieval built in to the assistant. The standard `agent` architecture performs RAG by including the Retrieval tool in the assistant configuration, like so:

```json
(...)
"tools": [
  {
      "type": "retrieval",
      "description": "Look up information in uploaded files.",
      "name": "Retrieval",
      "config": {
          "encoder": {
              "provider": "ollama",
              "dimensions": 384, 
              "encoder_model": "all-minilm"
          },
          "enable_rerank": true,
          "index_name": "test"
      },
      "multi_use": false 
  }
],
(...)
```
Currently, the supported encoders include: Cohere, OpenAI, Ollama, Azure OpenAI, and Mistral, but any encoder that is supported by langchain can be added by creating an adapter class:

```python
from typing import List
from pydantic import Field
from semantic_router.encoders import BaseEncoder
from langchain_community.embeddings import OllamaEmbeddings
from stack.app.core.configuration import settings

class OllamaEncoder(BaseEncoder):
    name: str = Field(default="all-minilm")
    score_threshold: float = Field(default=0.5)
    type: str = Field(default="ollama")
    dimensions: int = Field(default=384)
    embeddings: OllamaEmbeddings = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if "name" in data:
            self.embeddings = OllamaEmbeddings(
                model=self.name, base_url=settings.OLLAMA_BASE_URL
            )

    def __call__(self, docs: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(docs)
```

## Stand-alone Querying

Document retrieval can also be done independent of an assistant by calling the `/api/v1/rag/query` endpoint. This is a POST request with a JSON payload containing the query parameters. Here is an example of a query payload:

```json
{
  "input": "datasets used in experiments",
  "vector_database": {
    "type": "qdrant",
    "config": {
      "host": "http://localhost:6333",
      "api_key": "123456789"
    }
  },
  "encoder": {
    "provider": "ollama",
    "encoder_model": "nomic-embed-text",
    "dimensions": 768
  },
  "thread_id": "1924572b-042c-4725-b378-7e8c6664dc81",
  "exclude_fields": [],
  "enable_rerank": true
}
```

**Notes**

- `vector_database`: This block is optional but is useful when collections are held across different vector databases. If omitted, these details will be obtained from environment variables.
- `thread_id`: This is an optional parameter and can be used to tie the query to an existing conversation id for logging purposes.
- `enable_rerank`: Whether or not to rerank the query results. Currently requires a cohere api key if true (local reranking will be included in an upcoming release).

