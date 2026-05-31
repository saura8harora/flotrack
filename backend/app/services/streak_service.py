from datetime import date, timedelta

from bson import ObjectId

from app.config.database import get_database
from app.utils.helpers import today_str


async def check_and_reset_streak(user_id: str) -> None:
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return

    today = date.today()
    yesterday = today - timedelta(days=1)
    last_streak_date = user.get("last_streak_date")

    if not last_streak_date:
        return

    last_date = date.fromisoformat(last_streak_date)
    if last_date < yesterday and user.get("current_streak", 0) > 0:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"current_streak": 0}},
        )


async def update_streak_on_completion(user_id: str) -> int:
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return 0

    today = today_str()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    last_streak_date = user.get("last_streak_date")
    current_streak = user.get("current_streak", 0)

    if last_streak_date == today:
        return current_streak

    if last_streak_date == yesterday:
        new_streak = current_streak + 1
    else:
        new_streak = 1

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"current_streak": new_streak, "last_streak_date": today}},
    )

    return new_streak
