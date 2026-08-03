from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, index=True)

    owner = relationship("User", back_populates="workout_plans")
    items = relationship("WorkoutPlanItem", back_populates="workout_plan", cascade="all, delete-orphan")

class WorkoutPlanItem(Base):
    __tablename__ = "workout_plan_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workout_plan_id: Mapped[int] = mapped_column(ForeignKey("workout_plans.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    
    # Optional overrides
    sets: Mapped[int] = mapped_column(nullable=True)
    reps: Mapped[int] = mapped_column(nullable=True)
    weight_kg: Mapped[float] = mapped_column(nullable=True)

    workout_plan = relationship("WorkoutPlan", back_populates="items")
    exercise = relationship("Exercise")
