import calendar
from datetime import date

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.config.database import get_database
from app.utils.dependencies import get_current_user_id
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/{year}/{month}")
async def get_month_calendar(year: int, month: int, user_id: str = Depends(get_current_user_id)):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month")

    db = get_database()
    user_oid = ObjectId(user_id)

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    from datetime import timedelta

    end_inclusive = end_date - timedelta(days=1)
    start_str = start_date.isoformat()
    end_str = end_inclusive.isoformat()

    tasks = await db.tasks.find(
        {
            "user_id": user_oid,
            "date": {"$gte": start_str, "$lte": end_str},
        }
    ).to_list(length=1000)

    habit_logs = await db.habit_logs.find(
        {
            "user_id": user_oid,
            "date": {"$gte": start_str, "$lte": end_str},
            "completed": True,
        }
    ).to_list(length=5000)

    notes = await db.notes.find({"user_id": user_oid}).to_list(length=500)

    day_map: dict[str, dict] = {}
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        day_str = date(year, month, day).isoformat()
        day_map[day_str] = {"tasks": 0, "habits": 0, "notes": 0}

    for task in tasks:
        d = task.get("date")
        if d in day_map:
            day_map[d]["tasks"] += 1

    for log in habit_logs:
        d = log.get("date")
        if d in day_map:
            day_map[d]["habits"] += 1

    for note in notes:
        created = note.get("created_at", "")[:10]
        if created in day_map:
            day_map[created]["notes"] += 1

    return {
        "year": year,
        "month": month,
        "days": day_map,
        "month_name": calendar.month_name[month],
    }


@router.get("/day/{day_date}")
async def get_day_detail(day_date: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    user_oid = ObjectId(user_id)

    tasks = await db.tasks.find({"user_id": user_oid, "date": day_date}).to_list(length=200)
    habits = await db.habits.find({"user_id": user_oid}).to_list(length=200)

    habit_ids = [h["_id"] for h in habits]
    completed_ids = set()
    if habit_ids:
        logs = await db.habit_logs.find(
            {
                "user_id": user_oid,
                "habit_id": {"$in": habit_ids},
                "date": day_date,
                "completed": True,
            }
        ).to_list(length=500)
        completed_ids = {str(log["habit_id"]) for log in logs}

    habits_with_status = []
    for habit in habits:
        serialized = serialize_doc(habit)
        serialized["completed"] = str(habit["_id"]) in completed_ids
        habits_with_status.append(serialized)

    notes = await db.notes.find({"user_id": user_oid}).to_list(length=200)
    day_notes = [serialize_doc(n) for n in notes if n.get("created_at", "")[:10] == day_date]

    return {
        "date": day_date,
        "tasks": [serialize_doc(t) for t in tasks],
        "habits": habits_with_status,
        "notes": day_notes,
    }
