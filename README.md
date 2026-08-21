# ML-Guardian 🛡️

**A Secure Multi-Agent AI System for Intelligent Machine Learning Guidance, Retrieval and Responsible ML Risk Assessment**

ML-Guardian is an Agentic AI platform that assists users throughout the Machine Learning problem-solving process. A multi-agent architecture analyzes ML tasks, retrieves reliable technical knowledge, evaluates privacy, security and Responsible AI risks, and produces transparent and explainable ML recommendations — complete with an **ML Risk Passport** for every major recommendation.

---

## 🏗️ Architecture

```
User → Security Layer → Orchestrator Agent
                            ├── ML Analysis Agent
                            ├── Knowledge Retrieval Agent (RAG)
                            └── Responsible AI Agent
                                    ↓
                            Explanation Agent → ML Risk Passport
```

### Agents
| Agent | Responsibility |
|-------|---------------|
| **Orchestrator** | Routes user queries, intent classification, coordinates sub-agents |
| **ML Analysis** | Task classification, model recommendation, preprocessing advice |
| **Knowledge Retrieval** | RAG pipeline — searches curated ML knowledge base via ChromaDB |
| **Responsible AI** | Bias detection, PII checks, fairness evaluation, explainability |
| **Explanation** | Combines all agent outputs into final response + ML Risk Passport |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| LLM | OpenAI API (GPT-4o-mini) |
| Embeddings | sentence-transformers |
| Vector DB | ChromaDB |
| Database | PostgreSQL |
| Auth | JWT (bcrypt) |
| NLP | spaCy (NER/PII), custom intent classifier |
| Deployment | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### Setup
```bash
# 1. Clone the repo
git clone <repo-url>
cd ml_gurdian

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

# 3. Run with Docker
docker-compose up --build

# 4. Access the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📁 Project Structure

```
ml_gurdian/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # App configuration
│   ├── auth/                   # JWT authentication
│   ├── models/                 # Database models
│   ├── agents/                 # AI agent modules
│   ├── nlp/                    # NLP: intent, PII, summarization
│   ├── rag/                    # RAG pipeline
│   ├── security/               # Prompt guard, rate limiter
│   ├── risk_passport/          # ML Risk Passport generator
│   └── routers/                # API endpoints
├── frontend/
│   └── src/
│       ├── pages/              # Login, Chat, Dashboard
│       ├── components/         # UI components
│       └── services/           # API client
├── knowledge-base/
│   ├── documents/              # ML docs, papers, guides
│   └── scripts/                # Ingestion scripts
├── docs/                       # Reports, architecture diagrams
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 👥 Contributors

| Member | Role |
|--------|------|
| Member 1 | Agent Orchestration + Prompt Security |
| Member 2 | Authentication + User Data/PII Protection |
| Member 3 | Responsible AI + NLP + Bias/Explainability |
| Member 4 | RAG + Vector DB + Retrieval/API Security |

---

## 📄 License

This project is developed for academic purposes as part of the Information Retrieval and Web Analytics (IT3041) module.
