import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import app.config.database as database
from app.config.database import close_mongo_connection, connect_to_mongo
from app.config.settings import settings
from app.routes import analytics, auth, calendar, dashboard, habits, notes, tasks

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
PUBLIC_DIR = ROOT_DIR / "public"
IS_VERCEL = os.getenv("VERCEL") == "1"
STATIC_DIR = PUBLIC_DIR if IS_VERCEL and PUBLIC_DIR.exists() else FRONTEND_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not IS_VERCEL:
        await connect_to_mongo()
        yield
        await close_mongo_connection()
    else:
        yield


app = FastAPI(title="FloTrack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ensure_database(request: Request, call_next):
    if request.url.path.startswith("/api") and request.url.path != "/api/health":
        if not settings.has_database_config:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "MONGO_URI is not configured. Add it in Vercel → Settings → Environment Variables.",
                },
            )
        if database.db is None:
            try:
                await connect_to_mongo()
            except Exception as exc:
                return JSONResponse(
                    status_code=503,
                    content={"detail": f"Database connection failed: {exc}"},
                )
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server error: {type(exc).__name__}: {exc}"},
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
    if settings.has_database_config and database.db is None:
        try:
            await connect_to_mongo()
        except Exception:
            pass

    return {
        "status": "ok",
        "service": "FloTrack API",
        "mongo_uri_set": settings.has_database_config,
        "jwt_secret_set": settings.has_jwt_config,
        "database": "connected" if database.db is not None else "disconnected",
        "connection_error": database.last_connection_error,
    }


if not IS_VERCEL:

    @app.get("/")
    async def root():
        return RedirectResponse(url="/login.html")

    if STATIC_DIR.exists():
        app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
        app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")

        ALLOWED_PAGES = {
            "login", "signup", "dashboard", "tasks", "calendar", "notes", "analytics", "index",
        }

        def _page_response(page_name: str) -> FileResponse:
            if page_name not in ALLOWED_PAGES:
                raise HTTPException(status_code=404, detail="Page not found")
            path = STATIC_DIR / f"{page_name}.html"
            if not path.exists():
                raise HTTPException(status_code=404, detail="Page not found")
            return FileResponse(path, media_type="text/html")

        @app.get("/{page_name}.html")
        async def serve_page(page_name: str):
            return _page_response(page_name)

        @app.get("/pages/{page_name}.html")
        async def serve_legacy_page(page_name: str):
            return _page_response(page_name)
