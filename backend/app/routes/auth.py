from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.config.database import get_database
from app.config.security import create_access_token, hash_password, verify_password
from app.schemas.user_schema import TokenResponse, UserLogin, UserResponse, UserSignup
from app.utils.dependencies import get_current_user
from app.utils.helpers import serialize_doc, utc_now
from app.utils.validators import is_valid_email, is_valid_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        xp=user.get("xp", 0),
        level=user.get("level", 1),
        current_streak=user.get("current_streak", 0),
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignup):
    if not is_valid_email(payload.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if not is_valid_password(payload.password):
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    db = get_database()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_doc = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "xp": 0,
        "level": 1,
        "current_streak": 0,
        "last_streak_date": None,
        "created_at": utc_now().isoformat(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    user = serialize_doc(user_doc)
    token = create_access_token(user["id"])

    return TokenResponse(access_token=token, user=_user_response(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    db = get_database()
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    serialized = serialize_doc(user)
    token = create_access_token(serialized["id"])

    return TokenResponse(access_token=token, user=_user_response(serialized))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_response(current_user)
