# AI Interview Intelligence Platform

An AI-driven platform that simulates realistic technical, behavioral, and coding
interviews — resume-aware question generation, dynamic follow-ups, voice
interaction, and recruiter-style evaluation reports.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system design and the
milestone roadmap.

## Stack

| Layer    | Choices |
|----------|---------|
| Frontend | React, TypeScript, Vite, Tailwind CSS v4, shadcn/ui, Framer Motion |
| Backend  | FastAPI, Python 3.12, SQLAlchemy, PostgreSQL, Redis, JWT |
| AI       | LangChain/LlamaIndex, Sentence Transformers, FAISS/ChromaDB, Whisper, TTS |
| Infra    | Docker, GitHub Actions, Nginx |

## Repo structure

```
backend/    FastAPI application (uv-managed)
frontend/   React + Vite application
docs/       Architecture notes and roadmap
docker-compose.yml   Local Postgres + Redis
```

## Local development

**Prerequisites:** Python 3.12, [uv](https://docs.astral.sh/uv/), Node.js 20+, Docker (for Postgres/Redis, added from Milestone 2 onward).

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Health check: http://127.0.0.1:8000/api/v1/health
Interactive docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (proxies `/api/*` to the backend on port 8000)

### Infra (Postgres + Redis)

```bash
docker compose up -d
```
