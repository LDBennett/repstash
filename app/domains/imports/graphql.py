import strawberry
from typing import Optional
from app.domains.imports.models import JobStatus
from arq.connections import create_pool, RedisSettings
from app.core.config import settings
from app.domains.imports.models import ImportJob
from app.core.database import AsyncSessionLocal

strawberry.enum(JobStatus)

@strawberry.type
class ImportJobType:
    id: int
    status: JobStatus

# Global redis pool
_redis_pool = None

async def get_redis_pool():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    return _redis_pool

@strawberry.type
class ImportMutation:
    @strawberry.mutation
    async def import_exercise(self, url: str, user_id: int) -> ImportJobType:
        # Create pending job in db
        async with AsyncSessionLocal() as session:
            job = ImportJob(status=JobStatus.PENDING, user_id=user_id, source_url=url)
            session.add(job)
            await session.commit()
            await session.refresh(job)
            
            # Enqueue task
            redis = await get_redis_pool()
            await redis.enqueue_job("import_url_task", job.id, url, user_id)
            
            return ImportJobType(
                id=job.id,
                status=job.status
            )
