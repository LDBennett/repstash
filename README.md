# RepStash

**RepStash** is a modern, high-energy fitness application that allows users to copy/paste social media exercise links (Instagram Reels, TikToks, YouTube Shorts) and automatically converts them into structured exercise cards using AI (Gemini Flash).

Think of it as a "Paprika for Exercise Moves" — focusing on friction-free capture, custom exercise collection, and structured form details.

## 🚀 Features

- **Link Ingestion:** Paste URLs from popular social media platforms.
- **AI-Powered Extraction:** Uses Gemini 2.5 Flash to automatically extract exercise steps, muscles targeted, and default parameters from videos.
- **Organized Exercise Library:** Automatically categories exercises and targets specific muscle groups.
- **Workout Planning:** Build custom workout routines from your saved exercises.

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **GraphQL:** Strawberry GraphQL
- **Database:** PostgreSQL (with `asyncpg`), Async SQLAlchemy 2.0, Alembic
- **Task Queue:** Arq or Celery with Redis backend
- **AI Extraction:** Gemini 2.5 Flash via `google-genai`
- **Video Processing:** `yt-dlp` and `httpx` (ephemeral memory streaming)

### Frontend
- **Framework:** Next.js (App Router) with React 18+ and TypeScript
- **Styling:** Tailwind CSS (Solar Amber theme)
- **Animations:** Framer Motion
- **Authentication:** Clerk

## 📂 Project Structure

```
repstash/
├── app/                         # Python FastAPI Backend
│   ├── api/                     # GraphQL API schema
│   ├── core/                    # App configuration and database setup
│   ├── domains/                 # Domain-driven features (users, exercises, etc.)
│   └── workers/                 # Background task queues
├── frontend/                    # Next.js Frontend Application
├── alembic/                     # Database migrations
├── tests/                       # Pytest test suite
└── docker-compose.yml           # Local Postgres & Redis containers
```

## 💻 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (for PostgreSQL and Redis)

### Backend Setup

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Infrastructure (Postgres & Redis):**
   ```bash
   docker-compose up -d
   ```

3. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Run the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Run Background Worker:**
   ```bash
   python -m app.workers.task_queue
   ```

### Frontend Setup

1. **Install Node Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the Next.js Development Server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## 🧪 Testing

To run the backend test suite, use `pytest`:

```bash
pytest -v tests/
```

## 📜 License

This project is licensed under the [MIT License](LICENSE).
