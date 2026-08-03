from collections.abc import Sequence
from typing import Optional, Union

from arq.connections import RedisSettings
from arq.cron import CronJob
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function
from app.core.config import settings
from app.core.database import AsyncSessionLocal

import app.domains.users.models
import app.domains.exercises.models
import app.domains.imports.models
import app.domains.workouts.models

from app.domains.imports.service import process_import_job

async def import_url_task(ctx, job_id: int, source_url: str, user_id: int):
    async with AsyncSessionLocal() as session:
        await process_import_job(session, job_id, source_url, user_id)

class WorkerSettings:
    functions: Sequence[Union[WorkerCoroutine, Function]] = [import_url_task]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    cron_jobs: Optional[Sequence[CronJob]] = None
    on_startup: Optional[StartupShutdown] = None
    on_shutdown: Optional[StartupShutdown] = None

if __name__ == '__main__':
    from arq.worker import run_worker
    run_worker(WorkerSettings)
    
