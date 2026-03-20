from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import settings

class VectorManager:
    """
    RAG system: This indexes our SOPs into a vector store.
    """
    def __init__(self, collection_name: str = "copassist_protocols"):
        self.collection_name = collection_name
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
        # Using in-memory Qdrant for the assessment demo
        self.client = QdrantClient(location=":memory:") 
        
        # Ensure collection exists before initializing the store
        self._ensure_collection()
        
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )

    def _ensure_collection(self):
        """ Creates the collection if it doesn't exist in memory. """
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            # We need to specify the vector size for the embedding model
            # Google's models/embedding-001 usually outputs 768 dimensions
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            print(f"Collection {self.collection_name} created.")

    async def index_protocols(self, protocol_file_path: str):
        """ Read our SOP file and put it into memory! """
        with open(protocol_file_path, "r") as f:
            content = f.read()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)
        docs = text_splitter.create_documents([content])
        self.vector_store.add_documents(docs)
        print(f"Indexed {len(docs)} SOP chunks for RAG.")

    async def search_protocols(self, query: str, k: int = 2):
        """ Quick retrieval for decision making. """
        return self.vector_store.similarity_search(query, k=k)

vector_manager = VectorManager()
