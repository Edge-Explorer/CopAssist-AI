from fastapi import FastAPI
from src.api.router import api_router

# Hey there! This is the main entry point for the CopAssist API.
# I used FastAPI because it generates the docs automatically which saved me a lot of time! - Neel
app = FastAPI(
    title="CopAssist AI",
    description="Intelligent Patrol & Surveillance System for Law Enforcement Support",
    version="0.1.0"
)

# Include the main API router
app.include_router(api_router, prefix="/api")

# Added this to startup so we can index the protocols into our Vector Store!
@app.on_event("startup")
async def startup_event():
    from src.vector_db.manager import vector_manager
    import os
    # Just checking if the SOP file exists before indexing
    if os.path.exists("./data/protocols.txt"):
        await vector_manager.index_protocols("./data/protocols.txt")
        print("Successfully indexed police SOPs for RAG!")
    else:
        print("Warning: Standard Operating Procedures file not found!")

@app.get("/")
async def root():
    return {"message": "Welcome to CopAssist AI API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
