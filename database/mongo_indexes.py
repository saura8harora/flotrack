import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

env_path = Path(__file__).resolve().parent.parent / "backend" / "app" / ".env"
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "flotrack_db")


async def create_indexes():
    if not MONGO_URI:
        print("Error: MONGO_URI not set in .env")
        sys.exit(1)

    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]

    await db.users.create_index("email", unique=True)
    await db.habits.create_index([("user_id", 1), ("created_at", -1)])
    await db.habit_logs.create_index([("user_id", 1), ("date", 1)])
    await db.habit_logs.create_index(
        [("habit_id", 1), ("user_id", 1), ("date", 1)], unique=True
    )
    await db.tasks.create_index([("user_id", 1), ("status", 1)])
    await db.tasks.create_index([("user_id", 1), ("date", 1)])
    await db.notes.create_index([("user_id", 1), ("created_at", -1)])

    print("MongoDB indexes created successfully.")
    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
