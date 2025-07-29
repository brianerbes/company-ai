from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import uuid4

import chromadb
from chromadb.types import Collection

if TYPE_CHECKING:
    from .adapters.base_adapter import BaseLLMAdapter


class MemoryManager:
    """
    Provides the sole, high-level interface for all interactions with a
    company's long-term knowledge system (vector database).
    """

    def __init__(self, company_root_path: Path, embed_adapter: BaseLLMAdapter):
        """
        Initializes the MemoryManager for a specific company.

        Args:
            company_root_path: The root path of the company's workspace.
            embed_adapter: The LLM adapter to use for generating embeddings.
        """
        memory_path = company_root_path / "memory"
        memory_path.mkdir(exist_ok=True)

        # Set up a persistent client for ChromaDB. Each company has its own.
        self._db_client = chromadb.PersistentClient(path=str(memory_path))
        self._collection: Collection = self._db_client.get_or_create_collection(
            name="declarative_memory"
        )
        self._embed_adapter = embed_adapter

    def memorize(self, text_to_remember: str, metadata: Dict[str, Any] | None = None):
        """
        Takes a string of text, embeds it, and stores it in the vector DB.

        In the future, this will be expanded to use the full Memory Curation
        Pipeline from the blueprint.

        Args:
            text_to_remember: The piece of information to be stored.
            metadata: Optional dictionary of metadata associated with the memory.
        """
        # TODO: Implement the full Memory Curation Pipeline (distillation, scoring).
        if not metadata:
            metadata = {}

        embedding = self._embed_adapter.generate_embedding(text_to_remember)

        self._collection.add(
            embeddings=[embedding],
            documents=[text_to_remember],
            metadatas=[metadata],
            ids=[str(uuid4())],
        )
        print(f"Memorized: '{text_to_remember}'")

    def recall(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search to find the most relevant memories for a query.

        Args:
            query: The query to search for.
            n_results: The maximum number of results to return.

        Returns:
            A list of dictionaries, where each dictionary represents a recalled memory.
        """
        # TODO: Implement the intelligent re-ranking from the blueprint.
        query_embedding = self._embed_adapter.generate_embedding(query)

        results = self._collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        # The result object from chromadb is nested. We extract the relevant parts.
        recalled_memories = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                recalled_memories.append(
                    {
                        "document": doc,
                        "distance": results["distances"][0][i],
                        "metadata": results["metadatas"][0][i],
                    }
                )
        return recalled_memories
