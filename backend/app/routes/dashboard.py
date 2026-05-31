from bson import ObjectId
from fastapi import APIRouter, Depends

from app.config.database import get_database
from app.services.streak_service import check_and_reset_streak
from app.utils.dependencies import get_current_user_id
from app.utils.helpers import serialize_doc, today_str

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(user_id: str = Depends(get_current_user_id)):
    await check_and_reset_streak(user_id)
    db = get_database()
    user_oid = ObjectId(user_id)
    today = today_str()

    user = await db.users.find_one({"_id": user_oid})
    habits = await db.habits.find({"user_id": user_oid}).to_list(length=200)
    tasks = await db.tasks.find({"user_id": user_oid}).to_list(length=200)

    habit_ids = [h["_id"] for h in habits]
    today_logs = []
    if habit_ids:
        today_logs = await db.habit_logs.find(
            {"user_id": user_oid, "habit_id": {"$in": habit_ids}, "date": today, "completed": True}
        ).to_list(length=500)

    completed_habit_ids = {str(log["habit_id"]) for log in today_logs}
    today_habits = []
    for habit in habits:
        serialized = serialize_doc(habit)
        serialized["completed_today"] = str(habit["_id"]) in completed_habit_ids
        today_habits.append(serialized)

    today_tasks = [serialize_doc(t) for t in tasks if t.get("date") == today or not t.get("date")]
    done_tasks = sum(1 for t in tasks if t.get("status") == "done")
    total_tasks = len(tasks)
    completed_habits = len(completed_habit_ids)
    total_habits = len(habits)

    productivity_score = 0
    if total_habits or total_tasks:
        habit_pct = (completed_habits / total_habits * 50) if total_habits else 0
        task_pct = (done_tasks / total_tasks * 50) if total_tasks else 0
        productivity_score = round(habit_pct + task_pct)

    return {
        "user": serialize_doc(user),
        "xp": user.get("xp", 0),
        "level": user.get("level", 1),
        "current_streak": user.get("current_streak", 0),
        "today_habits": today_habits,
        "today_tasks": today_tasks[:10],
        "productivity_summary": {
            "score": productivity_score,
            "habits_completed": completed_habits,
            "habits_total": total_habits,
            "tasks_done": done_tasks,
            "tasks_total": total_tasks,
        },
    }
