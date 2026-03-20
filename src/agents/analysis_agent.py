from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from src.core.config import settings

class AnalysisAgent:
    """
    The Analysis Agent adds contextual reasoning to the telemetry.
    It considers local ordinances (e.g., park curfew) and historical patterns.
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Analysis Agent. Your role is to detect patterns and anomalies in summarized CV telemetry. Correlate with time of day and typical urban safety scenarios. Decide if the situation violates common sense or specific law enforcement protocols."),
            ("user", "Current Local Time: {current_time}\nVision Summary: {vision_summary}")
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
