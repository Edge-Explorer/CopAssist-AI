from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings
from src.api.v1.endpoints import TelemetryData

class VisionAgent:
    """
    The Vision Agent processes raw telemetry from CV sensors.
    Its job is to summarize telemetry over a window, filter noise, 
    and highlight immediate threshold breaches.
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Vision Agent for CopAssist AI. Your task is to analyze raw CV telemetry and summarize the situation. Focus on person counts and crowd density. Be concise."),
            ("user", "Telemetry Data: {telemetry_json}")
        ])

    async def process_telemetry(self, telemetry: TelemetryData) -> str:
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"telemetry_json": telemetry.model_dump_json()})
        return response.content

vision_agent = VisionAgent()
