from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import every domain's models so SQLAlchemy's mapper registry can resolve
# string-based relationship() references (e.g. Exercise.owner -> "User")
# regardless of which test module runs first.
import app.domains.exercises.models  # noqa: F401
import app.domains.imports.models  # noqa: F401
import app.domains.users.models  # noqa: F401
import app.domains.workouts.models  # noqa: F401
from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole
from app.domains.exercises.schemas import (
    ExerciseExtraction,
    MuscleTarget,
)


def make_mock_session() -> AsyncMock:
    """An AsyncMock standing in for an AsyncSession. `add` is sync on the real
    AsyncSession (it's never awaited), so it's overridden with a plain
    MagicMock to match; every other method used here is genuinely async."""
    session = AsyncMock(spec=AsyncSession)
    session.get = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    # On this mock library version, AsyncMock(spec=AsyncSession).execute's
    # return value is itself an AsyncMock (recursively, for every attribute
    # accessed on it), so unawaited chains like `.scalars().first()` silently
    # hand back coroutines instead of values. Pin it to a synchronous,
    # "empty result" MagicMock by default so `Result`-style chaining
    # (.scalars().first(), .scalars().unique().all(), .scalar_one_or_none())
    # behaves like a real, empty SQLAlchemy Result — individual tests
    # override `session.execute.return_value`/`.side_effect` as needed.
    empty_scalars = MagicMock()
    empty_scalars.all.return_value = []
    empty_scalars.first.return_value = None
    empty_scalars.unique.return_value = empty_scalars
    empty_result = MagicMock()
    empty_result.scalars.return_value = empty_scalars
    empty_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=empty_result)
    return session


def make_sample_extraction() -> ExerciseExtraction:
    """The single exercise Gemini's structured output is expected to produce."""
    return ExerciseExtraction(
        title="Barbell Squat",
        description="A compound lower-body strength exercise.",
        category=ExerciseCategory.STRENGTH,
        equipment="BARBELL",
        steps=["Set the bar on your back", "Squat down", "Stand back up"],
        default_sets=3,
        default_reps=10,
        default_weight_kg=60.0,
        muscles=[MuscleTarget(muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)],
    )


@pytest.fixture
def mock_session() -> AsyncMock:
    return make_mock_session()


@pytest.fixture
def sample_extraction() -> ExerciseExtraction:
    return make_sample_extraction()
