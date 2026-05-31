from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None
last_connection_error: str | None = None


async def connect_to_mongo() -> None:
    global client, db, last_connection_error

    if not settings.has_database_config:
        last_connection_error = "MONGO_URI is not set"
        return

    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=10000)
        db = client[settings.DATABASE_NAME]
        await client.admin.command("ping")
        last_connection_error = None
    except Exception as exc:
        client = None
        db = None
        last_connection_error = str(exc)
        raise


async def close_mongo_connection() -> None:
    global client, db
    if client:
        client.close()
    client = None
    db = None


def get_database() -> AsyncIOMotorDatabase:
    if not settings.has_database_config:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="Server misconfigured: MONGO_URI is missing. Add it in Vercel Environment Variables.",
        )
    if db is None:
        from fastapi import HTTPException

        detail = "Database is not connected."
        if last_connection_error:
            detail = f"Database connection failed: {last_connection_error}"
        raise HTTPException(status_code=503, detail=detail)
    return db
