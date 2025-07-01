# knowledge_base.py

"""
This module manages the shared, long-term memory for all agents using a
vector database. This allows the system to remember key decisions and facts,
reducing redundant questions and grounding the agents in established context.
"""
import chromadb

class KnowledgeBase:
    """
    A wrapper around a vector database (ChromaDB) to provide simple
    methods for adding and searching for facts.
    """
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "company_knowledge"):
        """
        Initializes the KnowledgeBase.

        Args:
            db_path (str): Path to the persistent database directory.
            collection_name (str): Name of the collection to store facts in.
        """
        # Using a persistent client means the database will be saved to disk.
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create a "collection," which is like a table in a SQL database.
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Simple counter to ensure unique IDs for each fact.
        self.fact_id_counter = self.collection.count()
        print(f"KnowledgeBase initialized. Found {self.fact_id_counter} existing facts.")

    def add_fact(self, text: str):
        """
        Adds a new fact to the knowledge base. A "fact" is typically a
        definitive decision made during a conversation.

        Args:
            text (str): The string content of the fact to be added.
        """
        doc_id = f"fact_{self.fact_id_counter}"
        self.collection.add(
            documents=[text],
            ids=[doc_id]
        )
        self.fact_id_counter += 1
        print(f"[KnowledgeBase] Added fact: '{text}'")

    def search_fact(self, query: str, confidence_threshold: float = 0.75) -> str | None:
        """
        Searches for a relevant fact in the knowledge base using similarity search.

        Args:
            query (str): The question or topic to search for.
            confidence_threshold (float): The minimum similarity score to consider
                                         a fact relevant. ChromaDB uses L2 distance;
                                         a lower value is better (more similar).

        Returns:
            The text of the most relevant fact if it meets the threshold, otherwise None.
        """
        # Don't search if the collection is empty.
        if self.collection.count() == 0:
            return None

        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )
        
        # Check if the query returned any documents
        if not results['documents'] or not results['documents'][0]:
            return None

        distance = results['distances'][0][0]
        document = results['documents'][0][0]

        print(f"[KnowledgeBase] Searched for '{query}'. Found '{document}' with distance {distance:.4f}.")

        # The distance is a measure of dissimilarity (L2 norm). Lower is better.
        # A threshold of < 0.75 is a reasonably high confidence match.
        if distance < confidence_threshold:
            print(f"[KnowledgeBase] Confidence threshold met. Using fact.")
            return document
        
        print(f"[KnowledgeBase] Confidence threshold NOT met.")
        return None