from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Campos base que comparten varios schemas de Task."""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Lo que el cliente envía al crear una task."""
    pass


class TaskUpdate(BaseModel):
    """
    Lo que el cliente envía al actualizar (PATCH).
    Todos los campos son opcionales — solo se actualiza lo que viene.
    """
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    is_archived: bool | None = None


class TaskResponse(TaskBase):
    """Lo que la API devuelve al cliente."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_archived: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime