from bson import ObjectId

from app.config.database import get_database
from app.utils.helpers import calculate_level


async def award_xp(user_id: str, amount: int) -> dict:
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {}

    new_xp = max(0, user.get("xp", 0) + amount)
    new_level = calculate_level(new_xp)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"xp": new_xp, "level": new_level}},
    )

    return {"xp": new_xp, "level": new_level}
