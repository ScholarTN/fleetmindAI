from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.ai.embeddings import (
    embed_documents,
    embed_query,
)

CHROMA_PATH = Path("storage/chroma")
COLLECTION_NAME = "fleetmind_docs"


class EmbeddingFunction:
    def __call__(self, input: list[str]) -> list[list[float]]:
        return embed_documents(input)


def get_client() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection() -> Collection:
    client = get_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=EmbeddingFunction(),
        metadata={
            "description": "FleetMind AI Knowledge Base"
        },
    )


def add_documents(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    collection = get_collection()

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def similarity_search(
    query: str,
    n_results: int = 5,
):
    collection = get_collection()

    return collection.query(
        query_texts=[query],
        n_results=n_results,
    )


def delete_all() -> None:
    client = get_client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    
    