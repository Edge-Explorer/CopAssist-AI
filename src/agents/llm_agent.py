from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings
from src.vector_db.manager import vector_manager

class LLMAgent:
    """
    RAG-driven final decision. Looks at official Protocols to give a professional recommendation.
    I hooked this up to the vector store we indexed earlier!
    """
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=0,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Decision Agent. Using the protocols and analysis, recommend an action. Be specific: e.g. 'Dispatch patrol now' or 'Monitoring only'."),
            ("user", "Relevant Police Protocols: {protocols}\nAnalysis Result: {analysis_summary}")
        ])

    async def generate_alert(self, analysis_summary: str) -> dict:
        # 1. Search for SOPs in the vector store
        protocols = await vector_manager.search_protocols(analysis_summary)
        protocol_text = "\n".join([doc.page_content for doc in protocols])
        
        # 2. Final Decision
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "protocols": protocol_text,
            "analysis_summary": analysis_summary
        })
        
        return {
            "analysis": analysis_summary,
            "decision": response.content,
            "rag_context": protocol_text
        }

llm_agent = LLMAgent()
