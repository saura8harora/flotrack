# FloTrack

A productivity operating system combining habit tracking, calendar planning, task management, note taking, streak tracking, XP system, and analytics.

## Tech Stack

- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** Python, FastAPI, Pydantic, JWT Authentication
- **Database:** MongoDB Atlas

## Project Structure

```
FloTrack/
├── backend/
│   ├── app/
│   │   ├── config/       # Settings, database, security
│   │   ├── routes/       # API endpoints
│   │   ├── schemas/      # Pydantic models
│   │   ├── services/     # Business logic (XP, streaks, analytics)
│   │   └── utils/        # Helpers and dependencies
│   └── requirements.txt
├── frontend/
│   ├── pages/            # HTML pages
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript modules
└── database/
    └── mongo_indexes.py  # MongoDB index setup
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy environment variables:

```bash
cp app/.env.example app/.env
```

Edit `app/.env` with your MongoDB URI and JWT secret.

Create MongoDB indexes:

```bash
python ../database/mongo_indexes.py
```

Start the API server:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

Serve the frontend with any static file server. For example, using VS Code Live Server or Python:

```bash
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500/pages/login.html` in your browser.

> **Important:** Pages must be served from the `frontend/` folder (not `frontend/pages/`).
> The correct URL is `/pages/login.html`, not `/login.html`.

### Option B: Single server (backend serves frontend)

Start only the backend — it also serves the frontend:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/pages/login.html`

## Environment Variables

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB Atlas connection string |
| `DATABASE_NAME` | Database name (default: `flotrack_db`) |
| `JWT_SECRET` | Secret key for JWT token signing |
| `JWT_ALGORITHM` | JWT algorithm (default: `HS256`) |
| `JWT_EXPIRE_MINUTES` | Token expiry in minutes (default: 10080) |
| `CORS_ORIGINS` | Comma-separated allowed origins |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/dashboard` | Dashboard data |
| GET/POST | `/api/habits` | List/create habits |
| PUT/DELETE | `/api/habits/{id}` | Update/delete habit |
| POST | `/api/habits/{id}/toggle` | Toggle habit completion |
| GET/POST | `/api/tasks` | List/create tasks |
| PUT/DELETE | `/api/tasks/{id}` | Update/delete task |
| GET/POST | `/api/notes` | List/create notes |
| PUT/DELETE | `/api/notes/{id}` | Update/delete note |
| GET | `/api/calendar/{year}/{month}` | Monthly calendar data |
| GET | `/api/calendar/day/{date}` | Day detail panel |
| GET | `/api/analytics` | Analytics data |

## Features

- JWT authentication with protected routes
- Habit tracking with XP rewards and streak system
- Kanban-style task board (dump / later / done)
- Samsung Notes-style note taking with search
- Interactive calendar with day detail panel
- Analytics dashboard with charts and progress tracking
