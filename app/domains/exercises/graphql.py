import strawberry
from typing import List, Optional
from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole

# Strawberry Enums
strawberry.enum(ExerciseCategory)
strawberry.enum(MuscleName)
strawberry.enum(MuscleRole)

@strawberry.type
class ExerciseMuscleType:
    id: int
    muscle: MuscleName
    role: MuscleRole

@strawberry.type
class ExerciseType:
    id: int
    user_id: int
    title: str
    description: Optional[str]
    category: ExerciseCategory
    equipment: Optional[str]
    steps: Optional[List[str]]
    default_sets: Optional[int]
    default_reps: Optional[int]
    default_weight_kg: Optional[float]
    source_url: Optional[str]
    muscles: List[ExerciseMuscleType]
