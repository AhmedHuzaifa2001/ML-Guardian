import chromadb
from chromadb.utils import embedding_functions
from config import settings
import os

# Ensure the directory for ChromaDB exists
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

class MLKnowledgeBase:
    def __init__(self):
        # Initialize the ChromaDB client to save data to disk
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        
        # Use the sentence-transformers model specified in .env
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Get or create the collection (like a table in SQL)
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Add new documents to the knowledge base."""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, n_results: int = 3):
        """Search the knowledge base for the most relevant documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

# Create a single instance to be used across the app
knowledge_base = MLKnowledgeBase()


##Persistent Storage: It initializes a chromadb.PersistentClient 
# that saves your vector data directly to the local folder 
# specified in your settings. This ensures your knowledge base is 
# not wiped out every time you restart the FastAPI server