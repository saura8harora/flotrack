from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config.database import get_database
from app.schemas.note_schema import NoteCreate, NoteUpdate
from app.utils.dependencies import get_current_user_id
from app.utils.helpers import serialize_doc, utc_now

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("")
async def list_notes(
    user_id: str = Depends(get_current_user_id),
    q: str | None = Query(default=None),
):
    db = get_database()
    query: dict = {"user_id": ObjectId(user_id)}

    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]

    notes = await db.notes.find(query).sort("created_at", -1).to_list(length=500)
    return [serialize_doc(n) for n in notes]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = {
        "user_id": ObjectId(user_id),
        "title": payload.title.strip(),
        "content": payload.content,
        "created_at": utc_now().isoformat(),
    }
    result = await db.notes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.put("/{note_id}")
async def update_note(note_id: str, payload: NoteUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "title" in updates:
        updates["title"] = updates["title"].strip()

    result = await db.notes.find_one_and_update(
        {"_id": ObjectId(note_id), "user_id": ObjectId(user_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Note not found")

    return serialize_doc(result)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")

    result = await db.notes.delete_one({"_id": ObjectId(note_id), "user_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
