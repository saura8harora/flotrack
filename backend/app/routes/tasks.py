from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config.database import get_database
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.utils.dependencies import get_current_user_id
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    date: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
):
    db = get_database()
    query: dict = {"user_id": ObjectId(user_id)}
    if date:
        query["date"] = date
    if status_filter:
        query["status"] = status_filter

    tasks = await db.tasks.find(query).sort("_id", -1).to_list(length=500)
    return [serialize_doc(t) for t in tasks]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = {
        "user_id": ObjectId(user_id),
        "title": payload.title.strip(),
        "status": payload.status,
        "priority": payload.priority,
        "date": payload.date,
    }
    result = await db.tasks.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.put("/{task_id}")
async def update_task(task_id: str, payload: TaskUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "title" in updates and updates["title"]:
        updates["title"] = updates["title"].strip()

    result = await db.tasks.find_one_and_update(
        {"_id": ObjectId(task_id), "user_id": ObjectId(user_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    return serialize_doc(result)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")

    result = await db.tasks.delete_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
