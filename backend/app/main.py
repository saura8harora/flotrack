from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config.database import close_mongo_connection, connect_to_mongo
from app.config.settings import settings
from app.routes import analytics, auth, calendar, dashboard, habits, notes, tasks

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title="FloTrack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(habits.router)
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(calendar.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "FloTrack API"}


@app.get("/")
async def root():
    return RedirectResponse(url="/login.html")


if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    ALLOWED_PAGES = {"login", "signup", "dashboard", "tasks", "calendar", "notes", "analytics", "index"}

    def _page_response(page_name: str) -> FileResponse:
        if page_name not in ALLOWED_PAGES:
            raise HTTPException(status_code=404, detail="Page not found")
        path = FRONTEND_DIR / f"{page_name}.html"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Page not found")
        return FileResponse(path, media_type="text/html")

    @app.get("/{page_name}.html")
    async def serve_page(page_name: str):
        return _page_response(page_name)

    @app.get("/pages/{page_name}.html")
    async def serve_legacy_page(page_name: str):
        return _page_response(page_name)