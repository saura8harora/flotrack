from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    status: str = Field(default="dump", pattern="^(dump|later|done)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    date: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    status: str | None = Field(default=None, pattern="^(dump|later|done)$")
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    date: str | None = None


class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    priority: str
    date: str | None = None
