# Hide and Seek

A story driven scavenger hunt and riddle-solving platform for Bergen Community College campus events.

## Features
- Google OAuth authentication with JWT sessions
- Team creation, join requests, and membership locks
- Event registration, leaderboards, and timed events
- Challenge submissions with hint requests
- Admin tools for managing events and challenges

## Tech stack
- Frontend: React 19, Vite, Tailwind CSS, Zustand
- Backend: FastAPI, SQLAlchemy (async), PostgreSQL
- Auth: Google OAuth, JWT
- Infra: Docker, Postgres, optional Redis

## Repository structure
- `backend/` FastAPI service, DB models, API routes
- `frontend/` React app (Vite + Tailwind)
- `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE.md`

## Prerequisites
- Node.js 18+ (20+ recommended)
- Python 3.10+
- PostgreSQL 14+ (or Docker)
- Optional: Redis (service included in Docker compose)

## Quick start (local)

### 1) Backend
Create `backend/.env` using the example below, then:

```bash
cd backend
python -m pip install --upgrade pip
python -m pip install uv
uv venv
uv sync
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### 3) Login (development)
Set `DEBUG=true` in `backend/.env`, then use the dev login form in the UI. In production, Google OAuth is expected.

## Docker (backend + infra)
You can run Postgres, Redis, and the API via Docker:

```bash
cd backend
# Create backend/.env before starting
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Configuration
The backend reads environment variables from `backend/.env`.

```env
# App
APP_NAME=Hide and Seek
DEBUG=true
SECRET_KEY=change-me

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/has

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# Google OAuth (optional for production)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Frontend
FRONTEND_URL=http://localhost:5173

# Team settings
TEAM_LOCK_DAYS=60
MAX_TEAM_SIZE=4
MIN_TEAM_SIZE=1
JOIN_REQUEST_EXPIRY_HOURS=24
```

Notes:
- `DATABASE_URL`, `SECRET_KEY`, `JWT_ALGORITHM`, and `FRONTEND_URL` are required for a working backend.
- `DEBUG=true` enables the dev login endpoint.
- Database tables are created automatically on API startup.
- Redis is configured but not currently referenced by the backend code.

## API
- Base path: `/api`
- OpenAPI docs: `/docs`
- ReDoc: `/redoc`

Main resources include `auth`, `teams`, `events`, and `challenges`.

## Frontend scripts
Run from `frontend/`:
- `npm run dev` Start the development server
- `npm run build` Build for production
- `npm run preview` Preview production build
- `npm run lint` Lint the codebase

## Cloudflare Python Worker deploy note
For backend deploys with Wrangler Python Workers, dependencies must be in `backend/cf-requirements.txt` as plain package names only (no comments and no version specifiers).
Use a simple list, for example:

```bash
cd backend
cat cf-requirements.txt
```

## Contributing
See `CONTRIBUTING.md` for contribution guidelines and local development notes.

## Security
Please review `SECURITY.md` for vulnerability reporting.

## Code of Conduct
See `CODE_OF_CONDUCT.md`.

## License
See `LICENSE.md`.
