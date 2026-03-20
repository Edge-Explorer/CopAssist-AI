from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings
from src.api.v1.endpoints import TelemetryData

class VisionAgent:
    """
    Summarizes raw data from our CV model. 
    I kept this separate to filter out the noise before the analysis stage! - Neel
    """
    def __init__(self):
        # Using Gemini 1.5 because its context window is huge but we keep it small to save costs
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=0,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze this CV data and give me a plain-English summary of what's happening. Focus on person counts and crowd density. Keep it under 2 sentences for faster processing."),
            ("user", "CV Data: {telemetry_json}")
        ])

    async def process_telemetry(self, telemetry: TelemetryData) -> str:
        # Standard chain invocation
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"telemetry_json": telemetry.model_dump_json()})
        return response.content

vision_agent = VisionAgent()
