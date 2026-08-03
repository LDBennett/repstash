import strawberry
from typing import Sequence
from strawberry.experimental import pydantic as strawberry_pydantic
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
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
            
        async with AsyncSessionLocal() as session:
            # Eagerly load the muscles relationship so we can return them
            stmt = select(Exercise).where(Exercise.user_id == user.id).options(selectinload(Exercise.muscles))
            result = await session.execute(stmt)
            exercises = result.scalars().all()
            return [ExerciseType.from_pydantic(ExerciseRead.model_validate(e)) for e in exercises]

    @strawberry.field
    async def exercise(self, info: strawberry.Info, id: int) -> ExerciseType:
        from app.domains.exercises.models import Exercise
        async with AsyncSessionLocal() as session:
            stmt = select(Exercise).where(Exercise.id == id).options(selectinload(Exercise.muscles))
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
            
        async with AsyncSessionLocal() as session:
            stmt = select(Exercise).where(Exercise.id == id).options(selectinload(Exercise.muscles))
            result = await session.execute(stmt)
            exercise = result.scalar_one_or_none()
            
            if not exercise:
                raise Exception("Exercise not found")
                
            if exercise.user_id != user.id:
                raise Exception("Unauthorized: you can only edit your own exercises")
                
            if description is not None:
                exercise.description = description
            if steps is not None:
                exercise.steps = steps
                
            await session.commit()
            await session.refresh(exercise)
            
            return ExerciseType.from_pydantic(ExerciseRead.model_validate(exercise))
