from pydantic import BaseModel, Field
from typing import Any, Optional, Literal

class SubmitTaskRequest(BaseModel):
    task_type: str = Field(default="demo")
    data: dict[str, Any] = Field(default_factory=dict)

class SubmitTaskResponse(BaseModel):
    task_id: str
    status: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    attempts: int
    result: Optional[dict] = None
    error: Optional[str] = None
