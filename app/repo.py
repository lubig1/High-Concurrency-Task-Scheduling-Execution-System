import json
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task, TaskStatus, Outbox

async def get_task_by_idempotency(db: AsyncSession, idem_key: str) -> Task | None:
    res = await db.execute(select(Task).where(Task.idempotency_key == idem_key))
    return res.scalar_one_or_none()

async def create_task_with_outbox(db: AsyncSession, idem_key: str, payload: dict) -> Task:
    task = Task(
        id=str(uuid4()),
        idempotency_key=idem_key,
        status=TaskStatus.PENDING,
        payload_json=json.dumps(payload),
        attempts=0,
    )
    db.add(task)
    db.add(Outbox(task_id=task.id, event_type="ENQUEUE_TASK", processed=False))
    await db.flush()  # 让 task.id 可用
    return task

async def mark_task_status(db: AsyncSession, task_id: str, status: TaskStatus, *, result=None, error=None, attempts=None):
    values = {"status": status}
    if result is not None:
        values["result_json"] = json.dumps(result)
    if error is not None:
        values["error"] = error
    if attempts is not None:
        values["attempts"] = attempts
    await db.execute(update(Task).where(Task.id == task_id).values(**values))

async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    res = await db.execute(select(Task).where(Task.id == task_id))
    return res.scalar_one_or_none()
