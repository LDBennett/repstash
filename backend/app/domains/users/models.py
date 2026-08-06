import enum
from datetime import date
from sqlalchemy import String, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class UnitPreference(str, enum.Enum):
    metric = "metric"
    imperial = "imperial"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    unit_preference: Mapped[UnitPreference] = mapped_column(Enum(UnitPreference), default=UnitPreference.metric)
    
    ai_usage_count: Mapped[int] = mapped_column(default=0)
    last_ai_usage_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    exercises = relationship("Exercise", back_populates="owner", cascade="all, delete-orphan")
    workout_plans = relationship("WorkoutPlan", back_populates="owner", cascade="all, delete-orphan")
