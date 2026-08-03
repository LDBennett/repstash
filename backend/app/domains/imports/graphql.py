import strawberry
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
    async def import_exercise(self, info: strawberry.Info, url: str) -> ImportJobType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")
            
        # Create pending job in db
        async with AsyncSessionLocal() as session:
            job = ImportJob(status=JobStatus.PENDING, user_id=user.id, source_url=url)
            session.add(job)
            await session.commit()
            await session.refresh(job)
            
            # Enqueue task
            redis = await get_redis_pool()
            await redis.enqueue_job("import_url_task", job.id, url, user.id)
            
            return ImportJobType(
                id=job.id,
                status=job.status
            )

@strawberry.type
class ImportQuery:
    @strawberry.field
    async def import_job(self, info: strawberry.Info, id: int) -> ImportJobType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")
            
        async with AsyncSessionLocal() as session:
            job = await session.get(ImportJob, id)
            if not job or job.user_id != user.id:
                raise Exception("Job not found or unauthorized")
                
            return ImportJobType(id=job.id, status=job.status)
