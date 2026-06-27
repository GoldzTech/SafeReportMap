# SafeReport Map

SafeReport Map is an AI-powered anonymous reporting platform designed for educational institutions. It helps transform anonymous reports into structured information, supporting administrators in identifying patterns, prioritizing cases, and improving institutional response.

## Features

- Anonymous public reporting
- AI-powered triage
- Automatic severity classification
- Priority score calculation
- Administrative dashboard
- Heatmap visualization
- Analytics dashboard
- CSV/PDF export
- JWT authentication
- Multi-tenant foundation

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### AI
- OpenAI API
- Rule-based pipeline
- Hybrid inference

## Project Structure

```
SafeReportMap/
├── frontend/
├── backend/
├── ai/
└── docker-compose.yml
```

## Running locally

### Backend

```bash
cd backend

source .venv/bin/activate

PYTHONPATH=. uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

## Status

Current stage:

- ✅ Local MVP completed
- 🚧 Cloud deployment in progress

## Author

Miguel Ribeiro de Sousa