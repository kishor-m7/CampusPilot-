# CampusPilot 🎓🚀

> **Intelligent Academic Co-pilot & Unified Command Center for University Students**

CampusPilot combines academic SaaS productivity utilities (assignments, exam schedules, study planners, velocity tracking) with an AI assistant powered by Gemini and an MCP (Model Context Protocol) server ready for voice assistants (such as Amazon Alexa).

---

## 🌟 Key Features

- **📊 Unified Command Center**: Consolidated view of upcoming assignment deadlines, exams, urgent reminders, and weekly study velocity.
- **🤖 Context-Aware AI Copilot**: Dedicated conversational assistant powered by Google Gemini, capable of syllabus breakdown, task creation, schedule optimization, and study coaching.
- **🎙️ Alexa & MCP Integration**: Model Context Protocol (MCP) server endpoints exposing real-time schedule, assignments, and study session tools for voice assistant integration.
- **📅 Smart Study Planner & Timetable**: Block time for deep work, track completed sessions, and monitor GPA projections.
- **⚡ Dual Database Architecture**: High-performance PostgreSQL via Supabase with automatic offline fallback to local SQLite.
- **🎨 Editorial Academic UI**: Minimalist, high-readability design system calibrated for long focus sessions across desktop and mobile.

---

## 🏗️ Architecture & Technology Stack

```
CampusPilot
├── backend/                  # FastAPI REST & MCP Backend
│   ├── routers/              # Modular API endpoints (overview, exams, assignments, etc.)
│   ├── agent.py              # Gemini LLM study assistant & tool orchestration
│   ├── database.py           # Dual Supabase PostgreSQL / SQLite persistence layer
│   ├── mcp_server.py         # MCP protocol server for Alexa / external integrations
│   └── models.py             # Pydantic schemas and data contracts
├── client/                   # Modern React + Vite Single Page Application
├── frontend/                 # Standalone static editorial HTML/CSS templates
├── supabase/migrations/      # Production SQL schema & migrations
├── scripts/                  # Automated database migration and seed scripts
└── tests/                    # Security, API, MCP, and agent unit tests
```

### Core Technologies
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, `asyncpg`, `google-genai`, `mcp`
- **Frontend / Client**: React, Vite, Tailwind CSS, Material Symbols Outlined
- **Database**: Supabase (PostgreSQL with Row Level Security) / Local SQLite
- **DevOps**: Docker, Docker Compose

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Git

### 2. Environment Configuration
Clone the repository and copy the environment template:
```bash
git clone https://github.com/kishor-m7/CampusPilot-.git
cd CampusPilot-
cp .env.example .env
```
Edit `.env` to configure your Gemini API key and database credentials:
```env
ENVIRONMENT=development
PORT=8000
DATABASE_URL=postgresql://... (or leave blank to use local SQLite)
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Backend Setup
Create and activate a virtual environment, then install dependencies:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Run the backend server:
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Client (Frontend) Setup
In a new terminal:
```bash
cd client
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🐳 Docker Deployment

You can run the entire stack with Docker Compose:
```bash
docker-compose up --build
```
This boots up the FastAPI backend and maps port 8000 to your host machine.

---

## 🧪 Running Tests

CampusPilot includes a comprehensive test suite covering API endpoints, MCP server tools, agent workflows, and security/injection sanitization:
```bash
pytest tests/ -v
```

---

## 📖 Documentation
- [Architecture & Design Tokens](docs/DESIGN.md)
- [API Contract Specification](docs/API_CONTRACT.md)
- [Supabase Setup & Migration Guide](docs/SUPABASE_SETUP.md)
- [AWS & Production Deployment Guide](docs/AWS_DEPLOYMENT.md)
- [Developer Handover Guide](HANDOVER.md)

---

## 📄 License
This project is licensed under the MIT License.
