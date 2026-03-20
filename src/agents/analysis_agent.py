from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from src.core.config import settings

class AnalysisAgent:
    """
    Decides if the situation is actually weird or just normal city life (using time of day).
    """
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=0.7,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an analyzer for CopAssist. Considering the time and current crowd level, is this unusual? For example, 100 people at 3 AM is super weird. Be smart and brief!"),
            ("user", "Current Local Time: {current_time}\nSummary from Vision Agent: {vision_summary}")
        ])

    async def analyze(self, vision_summary: str) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "current_time": current_time,
            "vision_summary": vision_summary
        })
        return response.content

analysis_agent = AnalysisAgent()
