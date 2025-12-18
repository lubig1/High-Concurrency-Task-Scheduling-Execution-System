import json
import time
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import SessionLocal
from app.models import TaskStatus
from app import repo
from app.settings import settings

def _do_work(payload: dict) -> dict:
    # 你可以替换成实际业务逻辑：ETL / 调度 / 推理 / 调用外部服务等
    # demo: 模拟耗时
    time.sleep(1)
    return {"ok": True, "echo": payload}

def run_task(task_id: str):
    """
    RQ worker entrypoint (sync). 这里内部用 async session 执行 DB 更新。
    """
    import asyncio

    async def _run():
        async with SessionLocal() as db:  # type: AsyncSession
            task = await repo.get_task(db, task_id)
            if not task:
                return

            # at-least-once 场景：如果已成功，直接返回（幂等执行保护）
            if task.status == TaskStatus.SUCCEEDED:
                return

            attempts = (task.attempts or 0) + 1
            await repo.mark_task_status(db, task_id, TaskStatus.RUNNING, attempts=attempts)
            await db.commit()

            try:
                payload = json.loads(task.payload_json)
                result = _do_work(payload)
                await repo.mark_task_status(db, task_id, TaskStatus.SUCCEEDED, result=result)
                await db.commit()
            except Exception as e:
                err = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                # 简化重试：由 worker 自己决定是否“回滚到 QUEUED”
                if attempts < settings.WORKER_MAX_RETRIES:
                    await repo.mark_task_status(db, task_id, TaskStatus.QUEUED, error=err, attempts=attempts)
                else:
                    await repo.mark_task_status(db, task_id, TaskStatus.FAILED, error=err, attempts=attempts)
                await db.commit()

    asyncio.run(_run())
