from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import settings

class VectorManager:
    """
    Handles indexing of police protocols for RAG.
    """
    def __init__(self, collection_name: str = "police_protocols"):
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        # Use local persistent storage or in-memory if no host
        self.client = QdrantClient(location=":memory:") 
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )

    async def index_protocols(self, protocol_file_path: str):
        with open(protocol_file_path, "r") as f:
            content = f.read()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.create_documents([content])
        self.vector_store.add_documents(docs)
        print(f"Indexed {len(docs)} protocol chunks.")

    async def search_protocols(self, query: str, k: int = 3):
        return self.vector_store.similarity_search(query, k=k)

vector_manager = VectorManager()
