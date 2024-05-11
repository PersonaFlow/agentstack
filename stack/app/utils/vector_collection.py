from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


def create_assistants_collection(
    client: QdrantClient, collection_name: str, dimension: int
):
    """Creates the collection for embeddings that use the Retrieval assistants
    tool."""
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "default": rest.VectorParams(
                size=dimension,
                distance=rest.Distance.COSINE,
            )
        },
        optimizers_config=rest.OptimizersConfigDiff(
            indexing_threshold=0,
        ),
    )

    client.create_payload_index(
        collection_name=collection_name,
        field_name="namespace",
        field_schema="keyword",
    )

    client.create_payload_index(
        collection_name=collection_name,
        field_name="file_id",
        field_schema="keyword",
    )
