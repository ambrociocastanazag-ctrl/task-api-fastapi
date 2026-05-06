from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ───────────────────────────────────────────────────────────────
#  Helper: get task and verify ownership
# ───────────────────────────────────────────────────────────────

def _get_owned_task(task_id: int, user: User, db: Session) -> Task:
    """
    Devuelve la task si pertenece al usuario actual.
    Si no existe O pertenece a otro usuario, lanza 404.
    Patrón de seguridad: no revelamos si el ID existe pero pertenece a otro.
    """
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == user.id)
        .first()
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


# ───────────────────────────────────────────────────────────────
#  CRUD Endpoints
# ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva task asignada al usuario autenticado."""
    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status.value,
        priority=payload.priority.value,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    include_archived: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Lista tasks del usuario actual.
    Soporta filtro por status, paginación, y opción de incluir archivadas.
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter.value)

    if not include_archived:
        query = query.filter(Task.is_archived.is_(False))

    return (
        query.order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve una task específica del usuario."""
    return _get_owned_task(task_id, current_user, db)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza parcialmente una task.
    Solo se modifican los campos que vengan en el body.
    """
    task = _get_owned_task(task_id, current_user, db)

    update_data = payload.model_dump(exclude_unset=True)

    # Convertir enums a sus valores string antes de guardar
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value
    if "priority" in update_data and update_data["priority"] is not None:
        update_data["priority"] = update_data["priority"].value

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una task del usuario actual."""
    task = _get_owned_task(task_id, current_user, db)
    db.delete(task)
    db.commit()
    return None