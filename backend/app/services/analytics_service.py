from datetime import date, timedelta

from bson import ObjectId

from app.config.database import get_database


async def get_analytics(user_id: str) -> dict:
    db = get_database()
    user_oid = ObjectId(user_id)
    today = date.today()

    habits = await db.habits.find({"user_id": user_oid}).to_list(length=500)
    habit_ids = [h["_id"] for h in habits]

    total_habits = len(habits)
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)

    week_logs = []
    month_logs = []
    if habit_ids:
        week_logs = await db.habit_logs.find(
            {
                "user_id": user_oid,
                "habit_id": {"$in": habit_ids},
                "date": {"$gte": week_start.isoformat(), "$lte": today.isoformat()},
                "completed": True,
            }
        ).to_list(length=5000)

        month_logs = await db.habit_logs.find(
            {
                "user_id": user_oid,
                "habit_id": {"$in": habit_ids},
                "date": {"$gte": month_start.isoformat(), "$lte": today.isoformat()},
                "completed": True,
            }
        ).to_list(length=10000)

    today_logs = [log for log in week_logs if log["date"] == today.isoformat()]
    today_completed = len(today_logs)
    habit_completion_pct = round((today_completed / total_habits * 100) if total_habits else 0, 1)

    weekly_progress = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        count = sum(1 for log in week_logs if log["date"] == day_str)
        weekly_progress.append({"date": day_str, "label": day.strftime("%a"), "completions": count})

    monthly_progress = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        count = sum(1 for log in month_logs if log["date"] == day_str)
        monthly_progress.append({"date": day_str, "completions": count})

    user = await db.users.find_one({"_id": user_oid})
    xp = user.get("xp", 0) if user else 0
    level = user.get("level", 1) if user else 1
    current_streak = user.get("current_streak", 0) if user else 0

    xp_history = []
    running_xp = max(0, xp - len(month_logs) * 10)
    for entry in monthly_progress:
        day_xp = entry["completions"] * 10
        running_xp += day_xp
        xp_history.append({"date": entry["date"], "xp": running_xp})

    if xp_history:
        xp_history[-1]["xp"] = xp

    streak_history = []
    for entry in weekly_progress:
        streak_history.append(
            {
                "date": entry["date"],
                "label": entry["label"],
                "active": entry["completions"] > 0,
            }
        )

    return {
        "habit_completion_percentage": habit_completion_pct,
        "total_habits": total_habits,
        "today_completions": today_completed,
        "weekly_progress": weekly_progress,
        "monthly_progress": monthly_progress,
        "xp": xp,
        "level": level,
        "xp_growth": xp_history[-7:] if xp_history else [],
        "current_streak": current_streak,
        "streak_history": streak_history,
    }
