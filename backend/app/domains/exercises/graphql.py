import strawberry
from typing import Sequence
from strawberry.experimental import pydantic as strawberry_pydantic
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.domains.exercises.models import Exercise, ExerciseCategory, MuscleName, MuscleRole, ExerciseEquipment
from app.domains.exercises.schemas import ExerciseRead, ExerciseMuscleRead

# Strawberry Enums
strawberry.enum(ExerciseCategory)
strawberry.enum(MuscleName)
strawberry.enum(MuscleRole)
strawberry.enum(ExerciseEquipment)

@strawberry_pydantic.type(model=ExerciseMuscleRead, all_fields=True)
class ExerciseMuscleType:
    pass

@strawberry_pydantic.type(model=ExerciseRead, all_fields=True)
class ExerciseType:
    pass

@strawberry.type
class ExerciseQuery:
    @strawberry.field
    async def my_exercises(self, info: strawberry.Info) -> Sequence[ExerciseType]:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")

        session = info.context["session"]
        # Eagerly load the muscles relationship so we can return them
        stmt = select(Exercise).where(Exercise.user_id == user.id, Exercise.deleted_at.is_(None)).options(selectinload(Exercise.muscles))
        result = await session.execute(stmt)
        exercises = result.scalars().all()
        return [ExerciseType.from_pydantic(ExerciseRead.model_validate(e)) for e in exercises]

    @strawberry.field
    async def exercise(self, info: strawberry.Info, id: int) -> ExerciseType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")

        session = info.context["session"]
        stmt = (
            select(Exercise)
            .where(Exercise.id == id, Exercise.user_id == user.id, Exercise.deleted_at.is_(None))
            .options(selectinload(Exercise.muscles))
        )
        result = await session.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise Exception("Exercise not found")

        return ExerciseType.from_pydantic(ExerciseRead.model_validate(exercise))

@strawberry.type
class ExerciseMutation:
    @strawberry.mutation
    async def update_exercise(self, info: strawberry.Info, id: int, description: str | None = None, steps: list[str] | None = None) -> ExerciseType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")

        session = info.context["session"]
        stmt = (
            select(Exercise)
            .where(Exercise.id == id, Exercise.user_id == user.id, Exercise.deleted_at.is_(None))
            .options(selectinload(Exercise.muscles))
        )
        result = await session.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise Exception("Exercise not found")

        if description is not None:
            exercise.description = description
        if steps is not None:
            exercise.steps = steps

        await session.commit()
        await session.refresh(exercise)

        return ExerciseType.from_pydantic(ExerciseRead.model_validate(exercise))

    @strawberry.mutation
    async def delete_exercise(self, info: strawberry.Info, id: int) -> bool:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: valid Clerk token required")

        session = info.context["session"]
        stmt = select(Exercise).where(Exercise.id == id, Exercise.user_id == user.id, Exercise.deleted_at.is_(None))
        result = await session.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            raise Exception("Exercise not found")

        exercise.deleted_at = datetime.now(timezone.utc)
        await session.commit()

        return True
