from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config.database import get_database
from app.schemas.habit_schema import HabitCreate, HabitUpdate
from app.services.streak_service import update_streak_on_completion
from app.services.xp_service import award_xp
from app.utils.dependencies import get_current_user_id
from app.utils.helpers import serialize_doc, today_str, utc_now

router = APIRouter(prefix="/api/habits", tags=["habits"])


async def _habit_with_completion(habit: dict, user_id: str, date: str | None = None) -> dict:
    db = get_database()
    check_date = date or today_str()
    log = await db.habit_logs.find_one(
        {
            "habit_id": habit["_id"],
            "user_id": ObjectId(user_id),
            "date": check_date,
            "completed": True,
        }
    )
    serialized = serialize_doc(habit)
    serialized["completed_today"] = log is not None
    if date:
        serialized["completed"] = log is not None
    return serialized


@router.get("")
async def list_habits(user_id: str = Depends(get_current_user_id)):
    db = get_database()
    habits = await db.habits.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).to_list(length=200)
    return [await _habit_with_completion(h, user_id) for h in habits]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_habit(payload: HabitCreate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = {
        "user_id": ObjectId(user_id),
        "title": payload.title.strip(),
        "category": payload.category.strip(),
        "xp_reward": payload.xp_reward,
        "created_at": utc_now().isoformat(),
    }
    result = await db.habits.insert_one(doc)
    doc["_id"] = result.inserted_id
    return await _habit_with_completion(doc, user_id)


@router.put("/{habit_id}")
async def update_habit(habit_id: str, payload: HabitUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(habit_id):
        raise HTTPException(status_code=400, detail="Invalid habit ID")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.habits.find_one_and_update(
        {"_id": ObjectId(habit_id), "user_id": ObjectId(user_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Habit not found")

    return await _habit_with_completion(result, user_id)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(habit_id):
        raise HTTPException(status_code=400, detail="Invalid habit ID")

    result = await db.habits.delete_one({"_id": ObjectId(habit_id), "user_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Habit not found")

    await db.habit_logs.delete_many({"habit_id": ObjectId(habit_id), "user_id": ObjectId(user_id)})


@router.post("/{habit_id}/toggle")
async def toggle_habit_completion(
    habit_id: str,
    user_id: str = Depends(get_current_user_id),
    date: str | None = Query(default=None),
):
    db = get_database()
    if not ObjectId.is_valid(habit_id):
        raise HTTPException(status_code=400, detail="Invalid habit ID")

    habit = await db.habits.find_one({"_id": ObjectId(habit_id), "user_id": ObjectId(user_id)})
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    target_date = date or today_str()
    existing = await db.habit_logs.find_one(
        {
            "habit_id": ObjectId(habit_id),
            "user_id": ObjectId(user_id),
            "date": target_date,
        }
    )

    xp_delta = 0
    completed = False

    if existing and existing.get("completed"):
        await db.habit_logs.update_one({"_id": existing["_id"]}, {"$set": {"completed": False}})
        xp_delta = -habit["xp_reward"]
        completed = False
    else:
        if existing:
            await db.habit_logs.update_one({"_id": existing["_id"]}, {"$set": {"completed": True}})
        else:
            await db.habit_logs.insert_one(
                {
                    "habit_id": ObjectId(habit_id),
                    "user_id": ObjectId(user_id),
                    "date": target_date,
                    "completed": True,
                }
            )
        xp_delta = habit["xp_reward"]
        completed = True
        await update_streak_on_completion(user_id)

    xp_data = await award_xp(user_id, xp_delta)
    updated_habit = await _habit_with_completion(habit, user_id, target_date)

    return {
        "habit": updated_habit,
        "completed": completed,
        "xp": xp_data.get("xp", 0),
        "level": xp_data.get("level", 1),
    }
