from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings
from src.vector_db.manager import vector_manager

class LLMAgent:
    """
    The LLM Agent performs RAG-based decision making.
    It takes the Analysis summary, searches for relevant Police Protocols,
    and produces a final Alert recommendation (severity and action).
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Decision Agent for CopAssist AI. Using the Analysis summary and retrieved Protocols, generate a final recommendation. Categorize severity as CRITICAL, WARNING, or INFO. Provide a specific 'recommended action' grounded in SOPs."),
            ("user", "Retrieved Protocols: {protocols}\nAnalysis Report: {analysis_summary}")
        ])

    async def generate_alert(self, analysis_summary: str) -> dict:
        # 1. Retrieve RAG context
        protocols = await vector_manager.search_protocols(analysis_summary)
        protocol_text = "\n".join([doc.page_content for doc in protocols])
        
        # 2. Invoke LLM
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "protocols": protocol_text,
            "analysis_summary": analysis_summary
        })
        
        # In a real app, use structured output or PydanticOutputParser
        # Simple string-for-now or JSON if requested
        return {
            "analysis": analysis_summary,
            "decision": response.content,
            "rag_context": protocol_text
        }

llm_agent = LLMAgent()
