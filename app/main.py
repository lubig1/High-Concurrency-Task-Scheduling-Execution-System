import time
from fastapi import FastAPI, Depends, Header
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.settings import settings
from app.logging_conf import configure_logging
from app.security import require_api_key
from app.rate_limit import rate_limit
from app.db import get_db, engine
from app.models import Base, TaskStatus
from app.schemas import SubmitTaskRequest, SubmitTaskResponse, TaskResponse
from app import repo, queue, metrics

configure_logging()
app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup():
    # 简化：启动时建表（面试/演示足够）。真正生产建议 Alembic migration
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/healthz")
async def healthz(db: AsyncSession = Depends(get_db)):
    # DB 连通性检查
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/metrics")
async def prom_metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

@app.post("/v1/tasks", dependencies=[Depends(require_api_key)], response_model=SubmitTaskResponse)
async def submit_task(
    req: SubmitTaskRequest,
    db: AsyncSession = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    x_client_id: str | None = Header(default="anonymous", alias="X-Client-Id"),
):
    # 限流（按 client_id）
    rate_limit(x_client_id or "anonymous", settings.RATE_LIMIT_PER_MINUTE)

    if not idempotency_key:
        # production 推荐强制要求，避免重复提交造成多次执行
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")

    existing = await repo.get_task_by_idempotency(db, idempotency_key)
    if existing:
        return SubmitTaskResponse(task_id=existing.id, status=existing.status.value)

    payload = {"task_type": req.task_type, "data": req.data}
    task = await repo.create_task_with_outbox(db, idempotency_key, payload)
    await db.commit()

    # Outbox dispatcher：可以做成独立进程/定时器；这里为了演示在请求内触发一次
    async with db.begin():
        n = await queue.dispatch_outbox(db, batch_size=20)
    metrics.TASK_SUBMITTED.inc()

    return SubmitTaskResponse(task_id=task.id, status=TaskStatus.QUEUED.value)

@app.get("/v1/tasks/{task_id}", dependencies=[Depends(require_api_key)], response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await repo.get_task(db, task_id)
    from fastapi import HTTPException
    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    result = None
    if task.result_json:
        import json
        result = json.loads(task.result_json)

    return TaskResponse(
        task_id=task.id,
        status=task.status.value,
        attempts=task.attempts,
        result=result,
        error=task.error,
    )
