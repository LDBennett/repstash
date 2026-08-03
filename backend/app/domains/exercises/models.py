import enum
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Enum
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ExerciseCategory(str, enum.Enum):
    STRENGTH = "STRENGTH"
    CARDIO = "CARDIO"
    MOBILITY = "MOBILITY"
    CALISTHENICS = "CALISTHENICS"
    HIIT = "HIIT"

class ExerciseEquipment(str, enum.Enum):
    BARBELL = "BARBELL"
    DUMBBELL = "DUMBBELL"
    KETTLEBELL = "KETTLEBELL"
    CABLE = "CABLE"
    MACHINE = "MACHINE"
    SMITH_MACHINE = "SMITH_MACHINE"
    BODYWEIGHT = "BODYWEIGHT"
    RESISTANCE_BAND = "RESISTANCE_BAND"
    OTHER = "OTHER"

class MuscleRole(str, enum.Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"

class MuscleName(str, enum.Enum):
    QUADRICEPS = "QUADRICEPS"
    HAMSTRINGS = "HAMSTRINGS"
    CALVES = "CALVES"
    GLUTES = "GLUTES"
    CHEST = "CHEST"
    LATS = "LATS"
    UPPER_BACK = "UPPER_BACK"
    TRICEPS = "TRICEPS"
    BICEPS = "BICEPS"
    ABS = "ABS"
    OBLIQUES = "OBLIQUES"
    LOWER_BACK = "LOWER_BACK"

class ExerciseMuscle(Base):
    __tablename__ = "exercise_muscles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    muscle: Mapped[MuscleName] = mapped_column(Enum(MuscleName))
    role: Mapped[MuscleRole] = mapped_column(Enum(MuscleRole))

    exercise = relationship("Exercise", back_populates="muscles")

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[ExerciseCategory] = mapped_column(Enum(ExerciseCategory))
    equipment: Mapped[Optional[ExerciseEquipment]] = mapped_column(Enum(ExerciseEquipment), nullable=True)
    steps: Mapped[Optional[list[str]]] = mapped_column(postgresql.ARRAY(String), nullable=True)
    
    default_sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    owner = relationship("User", back_populates="exercises")
    muscles = relationship("ExerciseMuscle", back_populates="exercise", cascade="all, delete-orphan")
