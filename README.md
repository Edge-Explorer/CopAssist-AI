# CopAssist AI – Intelligent Patrol & Surveillance System

CopAssist AI is an automated surveillance analysis platform designed to assist law enforcement. It combines real-time Computer Vision telemetry with a Multi-Agent LLM reasoning system (RAG) to provide contextual, protocol-based alerts.

## 🚀 Key Features

- **Computer Vision Telemetry**: Real-time monitoring of crowd density, person count, and unusual movements.
- **Multi-Agent Brain**: Decoupled agents for Vision, Analysis, and Decision-making.
- **RAG-Powered Alerts**: Alerts are grounded in official police protocols and safety manuals.
- **Smart Summarization**: Situational reports generated hourly or daily to reduce "alert fatigue."
- **Cost-Aware Prompting**: Optimized LLM interaction for lower latency and token usage.

## 🏗️ Architecture

```mermaid
graph TD
    A[Camera Feed] --> B[CV Model / Simulator]
    B --> C[Crowd Data & Telemetry]
    C --> D[Vision Agent]
    D --> E[Analysis Agent]
    E --> F[LLM Agent + RAG]
    G[Vector DB / Protocols] --> F
    F --> H[PostgreSQL Alerts]
    H --> I[FastAPI Dashboard / Alerts]
```

## 💰 Cost-Aware Prompting (Production Ready)

To maintain low latency and token costs, CopAssist uses a **Layered Intelligence** approach:
1.  **Vision Agent (Filter)**: Summarizes raw CV telemetry into human-readable snippets. This prevents second-stage agents from processing lengthy raw JSON.
2.  **Short-Session Context**: Agents use precise `ChatPromptTemplates` with instruction-only contexts.
3.  **Smart Escalation**: The decision agent only triggers RAG lookups if specific thresholds (e.g., population count or density anomalies) are breached.

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy)
- **Vector DB**: Qdrant / ChromaDB
- **LLM**: OpenAI (GPT-4o) / LangChain
- **CV**: OpenCV + YOLO (or Mock/HOG)
- **Package Manager**: UV

## ⚙️ Setup & Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/CopAssist-AI.git
    cd CopAssist-AI
    ```

2.  **Initialize Environment**:
    ```bash
    uv venv
    uv sync
    ```

3.  **Environment Variables**:
    Create a `.env` file:
    ```env
    OPENAI_API_KEY=your_key
    DATABASE_URL=postgresql://user:pass@localhost:5432/copassist
    QDRANT_HOST=localhost
    QDRANT_PORT=6333
    ```

4.  **Run the Server**:
    ```bash
    uv run uvicorn src.main:app --reload
    ```

## 🧠 Real-World Thinking: Case Study

**Scenario**: Unauthorized gathering at City Park at 2 AM.
- **Vision Agent**: Reports increase from 2 to 50 people within 10 minutes.
- **Analysis Agent**: Correlates with local ordinance (Park closes at 11 PM).
- **LLM Agent**: Consults RAG (Standard Operating Procedures) and generates a "Priority 1" alert recommending immediate patrol.

## 💥 Multi-Agent Collaboration

- **Vision Agent**: Filters noise and aggregates telemetry.
- **Analysis Agent**: Detects patterns and detects anomalies.
- **Decision Agent**: Maps patterns to protocols and communicates with humans.
