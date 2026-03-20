from qdrant_client import QdrantClient
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
        # Note: Using Google's embedding model to keep costs down and be consistent! - Neel
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
        self.client = QdrantClient(location=":memory:") 
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )

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
# I'll manually trigger indexing in a startup script later... - Neel
