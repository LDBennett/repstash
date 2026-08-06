from datetime import datetime, timezone
import strawberry
from app.domains.imports.models import JobStatus
from arq.connections import create_pool, RedisSettings
from app.core.config import settings
from app.domains.imports.models import ImportJob
from app.domains.users.models import User
from app.domains.exercises.models import Exercise
from sqlalchemy import select

strawberry.enum(JobStatus)

@strawberry.type
class ImportJobType:
    id: int
    status: JobStatus
    exercise_id: int | None = None

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
        session = info.context["session"]
        db_user = await session.get(User, user.id)

        # Check if this URL is already imported (deduplication)
        # If so, it won't consume an AI request, so we don't count it.
        existing_stmt = select(Exercise).where(Exercise.source_url == url)
        existing_result = await session.execute(existing_stmt)
        existing_exercise = existing_result.scalars().first()

        if not existing_exercise:
            # This will require AI. Check rate limits.
            today = datetime.now(timezone.utc).date()
            if db_user.last_ai_usage_date != today:
                db_user.ai_usage_count = 0
                db_user.last_ai_usage_date = today

            if db_user.ai_usage_count >= settings.DAILY_AI_IMPORT_LIMIT:
                raise Exception(f"Daily AI usage limit reached ({settings.DAILY_AI_IMPORT_LIMIT}/day). Please try again tomorrow.")

            db_user.ai_usage_count += 1
            session.add(db_user)

        job = ImportJob(status=JobStatus.PENDING, user_id=user.id, source_url=url)
        session.add(job)
        await session.commit()
        await session.refresh(job)

        # Enqueue task
        redis = await get_redis_pool()
        await redis.enqueue_job("import_url_task", job.id, url, user.id)

        return ImportJobType(
            id=job.id,
            status=job.status,
            exercise_id=job.exercise_id,
        )

@strawberry.type
class ImportQuery:
    @strawberry.field
    async def import_job(self, info: strawberry.Info, id: int) -> ImportJobType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")

        session = info.context["session"]
        job = await session.get(ImportJob, id)
        if not job or job.user_id != user.id:
            raise Exception("Job not found or unauthorized")

        return ImportJobType(id=job.id, status=job.status, exercise_id=job.exercise_id)
