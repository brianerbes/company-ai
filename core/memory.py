import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import uuid

class MemoryManager:
    """
    Manages the long-term contextual memory for a company using ChromaDB.
    """
    def __init__(self, company_root: Path):
        # Persist the memory database within the company's workspace directory
        db_path = company_root / "memory" / "chroma_db"
        self.client = chromadb.PersistentClient(path=str(db_path))
        
        # Initialize the model for creating vector embeddings
        # 'all-MiniLM-L6-v2' is a good, lightweight default model.
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create a collection for this company's memory
        self.collection = self.client.get_or_create_collection(name="contextual_memory")
        print(f"--- MemoryManager initialized. Using DB at: {db_path} ---")

    def memorize(self, text: str, metadata: dict = None):
        """
        Embeds a piece of text and stores it in the vector database.

        Args:
            text: The string of text to be memorized.
            metadata: A dictionary of metadata to associate with the text,
                      e.g., {'source': 'file.txt', 'agent_id': 'xyz'}.
        """
        if not text.strip():
            return # Don't memorize empty strings

        # Generate a unique ID for this memory entry
        doc_id = str(uuid.uuid4())
        
        # Create the vector embedding from the text
        embedding = self.embedding_model.encode(text).tolist()
        
        # Store the document, its embedding, and metadata in the collection
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            ids=[doc_id]
        )
        print(f"--- Memorized new context. Source: {metadata.get('source', 'unknown')} ---")

    def recall(self, query: str, n_results: int = 5) -> list[dict]:
        """
        Searches the memory for context relevant to a query.

        Args:
            query: The natural language query to search for.
            n_results: The maximum number of results to return.

        Returns:
            A list of result dictionaries, each containing the document and metadata.
        """
        if not query.strip():
            return []

        # Create a vector embedding for the search query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Query the collection for the most similar documents
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format and return the results
        recalled_memories = []
        if results and results.get('documents'):
            for i, doc in enumerate(results['documents'][0]):
                recalled_memories.append({
                    "document": doc,
                    "metadata": results['metadatas'][0][i]
                })
        
        print(f"--- Recalled {len(recalled_memories)} memories for query: '{query[:50]}...' ---")
        return recalled_memories