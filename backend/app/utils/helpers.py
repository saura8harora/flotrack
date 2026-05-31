from datetime import date, datetime, timezone
from typing import Any

from bson import ObjectId


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def today_str() -> str:
    return date.today().isoformat()


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def calculate_level(xp: int) -> int:
    return (xp // 100) + 1


def serialize_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if not doc:
        return None
    result = {**doc}
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    if "user_id" in result and isinstance(result["user_id"], ObjectId):
        result["user_id"] = str(result["user_id"])
    if "habit_id" in result and isinstance(result["habit_id"], ObjectId):
        result["habit_id"] = str(result["habit_id"])
    return result


def serialize_docs(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [serialize_doc(doc) for doc in docs if doc]
