from pydantic import BaseModel, Field
from typing import List, Optional
from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole

class MuscleTarget(BaseModel):
    muscle: MuscleName
    role: MuscleRole

class ExerciseExtraction(BaseModel):
    title: str = Field(description="A clear, concise name for the exercise")
    description: Optional[str] = Field(None, description="A detailed description of how to perform the exercise safely")
    category: ExerciseCategory = Field(description="The primary category of the exercise")
    equipment: Optional[str] = Field(None, description="Equipment required, e.g., 'Dumbbells', 'Kettlebell', 'Barbell'")
    steps: List[str] = Field(description="Step-by-step instructions to perform the exercise")
    default_sets: Optional[int] = Field(None, description="Suggested default number of sets")
    default_reps: Optional[int] = Field(None, description="Suggested default number of reps")
    default_weight_kg: Optional[float] = Field(None, description="Suggested default weight in kilograms (kg)")
    muscles: List[MuscleTarget] = Field(default_factory=list, description="Target muscles for the exercise")

class ExtractionResult(BaseModel):
    exercises: List[ExerciseExtraction] = Field(description="List of exercises extracted from the video or post")
