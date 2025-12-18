from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Outbox, TaskStatus
from app.settings import settings
from app import repo
import redis
from rq import Queue

redis_conn = redis.Redis.from_url(settings.REDIS_URL)
q = Queue("tasks", connection=redis_conn, default_timeout=settings.WORKER_DEFAULT_TIMEOUT_S)

async def dispatch_outbox(db: AsyncSession, batch_size: int = 50) -> int:
    res = await db.execute(select(Outbox).where(Outbox.processed == False).limit(batch_size))  # noqa: E712
    events = res.scalars().all()
    if not events:
        return 0

    for ev in events:
        # 入队：worker 会回写 DB 状态
        q.enqueue("app.worker.run_task", ev.task_id)
        await repo.mark_task_status(db, ev.task_id, TaskStatus.QUEUED)

    # 标记 processed（同一事务）
    ids = [e.id for e in events]
    await db.execute(update(Outbox).where(Outbox.id.in_(ids)).values(processed=True))
    return len(events)
