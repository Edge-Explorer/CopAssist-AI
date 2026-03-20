from fastapi import FastAPI
from src.api.router import api_router

app = FastAPI(
    title="CopAssist AI",
    description="Intelligent Patrol & Surveillance System for Law Enforcement Support",
    version="0.1.0"
)

# Include the main API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to CopAssist AI API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
