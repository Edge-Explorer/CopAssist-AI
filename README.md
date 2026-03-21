# 🚔 CopAssist AI — Intelligent Patrol & Surveillance System

> **Built for the CopMap AI Internship Assessment**
> A production-grade, Multi-Agent AI system for real-time law enforcement support.

---

## 🎯 What is CopAssist AI?

CopAssist AI is a **Real-Time Surveillance Intelligence Platform** that transforms a simple webcam into a smart patrol officer. It uses a **3-Stage Multi-Agent AI Pipeline** to:

1. **See** → Computer Vision detects people & analyzes behavior.
2. **Think** → Gemini 2.0 Flash reasons over police SOPs using RAG.
3. **Act** → Generates structured alerts and logs them to a database.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CopAssist AI — System Architecture              │
└─────────────────────────────────────────────────────────────┘
                             │
         ┌──────────────────┐│┌──────────────────┐
         │   CV Detector    │││   FastAPI Server  │
         │  (HOG + Haar +   │→│  (REST Endpoints) │
         │   MediaPipe Pose)│││                   │
         └──────────────────┘│└────────┬──────────┘
                              │         │
              ┌───────────────┼─────────▼────────────────┐
              │            Multi-Agent Brain              │
              │  ┌───────────────────────────────────┐   │
              │  │ 1. Vision Agent (Data Processor)  │   │
              │  │ 2. Analysis Agent (Context Reason)│   │
              │  │ 3. LLM Agent (RAG + Gemini 2.0)   │   │
              │  └─────────────────┬─────────────────┘   │
              └────────────────────┼────────────────────--┘
                                   │
              ┌────────────────────▼─────────────────────┐
              │          PostgreSQL Database              │
              │  • telemetry table (raw CV data)         │
              │  • alerts table (AI decisions)           │
              └──────────────────────────────────────────┘
```

---

## ✨ Key Features

| Feature | Technology | Description |
|---|---|---|
| **Multi-Mode Person Detection** | HOG + Haar Cascades | Identifies people sitting, standing, or walking |
| **Behavioral Threat Analysis** | MediaPipe Pose | Detects aggressive stances / raised hands = RED ALERT |
| **Multi-Agent LLM Reasoning** | Gemini 2.0 Flash | 3-stage pipeline: Vision → Analysis → Decision |
| **RAG-Based Intelligence** | Qdrant + Gemini Embeddings | AI follows real Police SOPs from `data/protocols.txt` |
| **Data Persistence** | PostgreSQL + SQLAlchemy + Alembic | Full audit trail of all detections and alerts |
| **Non-Blocking Architecture** | Python Threading | Webcam feed never lags during API calls |
| **API Documentation** | FastAPI (auto-generated) | Interactive Swagger UI at `/docs` |

---

## 🥊 Behavioral Threat Detection (MediaPipe)

Our newest feature upgrades the system from "counting" to **understanding**:

- **Skeleton Tracking**: MediaPipe tracks 33 body landmarks in real-time
- **Aggressive Stance Logic**: If wrists rise above shoulders → `AGGRESSIVE_STANCE` anomaly flagged
- **SOP-103 Trigger**: LLM automatically escalates to `IMMEDIATE RED ALERT` and recommends deploying a primary response unit
- **Visual Feedback**: Skeleton overlay + on-screen alert banner → perfect for demo!

---

## 🤖 The Multi-Agent Pipeline

### Agent 1: Vision Agent
Receives raw CV telemetry and filters noise. Normalizes data into a structured summary for downstream agents.

### Agent 2: Analysis Agent
Adds contextual reasoning — time of day, crowd patterns, past history flags. Detects anomalies vs. normal activity.

### Agent 3: LLM Agent (The Commander)
- Embeds the situation summary and searches **Qdrant** vector store
- Retrieves the most relevant Police SOP from `data/protocols.txt`
- Uses **Gemini 2.0 Flash** to generate a final severity-tagged alert + recommended action

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL (with `CopAssistAI` database created)
- A valid Google Gemini API key

### 1. Clone the Repository
```bash
git clone https://github.com/Edge-Explorer/CopAssist-AI.git
cd CopAssist-AI
```

### 2. Install Dependencies
```bash
pip install uv
uv sync
```

### 3. Configure Environment
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/CopAssistAI
```

### 4. Run Database Migrations
```bash
uv run alembic upgrade head
```

### 5. Start the API Server
```bash
uv run uvicorn src.main:app --reload
```

### 6. Start the CV Detector (in a new terminal)
```bash
uv run python src/cv/detector.py
```

### 7. View the API Docs
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

## 📁 Project Structure

```
CopAssist-AI/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── agents/
│   │   ├── vision_agent.py     # Agent 1: CV Data Processor
│   │   ├── analysis_agent.py   # Agent 2: Contextual Reasoner
│   │   └── llm_agent.py        # Agent 3: Gemini + RAG Commander
│   ├── api/v1/
│   │   └── endpoints.py        # REST API routes
│   ├── core/
│   │   └── config.py           # Settings & environment config
│   ├── cv/
│   │   └── detector.py         # HOG + Haar + MediaPipe detector
│   ├── db/
│   │   └── models.py           # SQLAlchemy models
│   └── vector_db/
│       └── manager.py          # Qdrant RAG manager
├── data/
│   └── protocols.txt           # Police SOP Knowledge Base (RAG source)
├── alembic/                    # DB migration scripts
├── .env                        # 🔒 Secret keys (NOT in Git)
├── pyproject.toml              # Python dependencies
└── README.md
```

---

## 🛡️ Security

- API keys are stored securely in `.env` (excluded from Git via `.gitignore`)
- All credentials are loaded via `pydantic-settings`
- Alembic manages all schema changes safely

---

## 📜 License

MIT License — See [LICENSE](./LICENSE) for details.

---

*Built with ❤️ Edge-Explorer for the CopMap AI Internship Assessment.*
