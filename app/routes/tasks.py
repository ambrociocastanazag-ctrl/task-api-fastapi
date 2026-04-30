"""Task endpoints — CRUD operations.

To be implemented on day 2:
    - GET    /tasks       List all tasks
    - POST   /tasks       Create a new task
    - GET    /tasks/{id}  Retrieve one task
    - PUT    /tasks/{id}  Update a task
    - DELETE /tasks/{id}  Delete a task
"""

from fastapi import APIRouter

router = APIRouter()
