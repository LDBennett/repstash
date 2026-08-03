from arq import Worker
from arq.connections import RedisSettings
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
    functions = [import_url_task]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

if __name__ == '__main__':
    import asyncio
    from arq.worker import run_worker
    asyncio.run(run_worker(WorkerSettings))
    
