from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    xp_reward: int = Field(ge=1, le=1000, default=10)


class HabitUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    xp_reward: int | None = Field(default=None, ge=1, le=1000)


class HabitResponse(BaseModel):
    id: str
    user_id: str
    title: str
    category: str
    xp_reward: int
    created_at: str
    completed_today: bool = False
