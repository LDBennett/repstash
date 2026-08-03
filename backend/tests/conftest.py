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
    ExtractionResult,
    MuscleTarget,
)


class FakeAsyncSessionCM:
    """Stands in for `async with AsyncSessionLocal() as session: ...`."""

    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, *exc_info):
        return False


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
    return session


def make_sample_extraction() -> ExtractionResult:
    """One exercise with one muscle target, matching what Gemini's structured
    output is expected to look like."""
    return ExtractionResult(
        exercises=[
            ExerciseExtraction(
                title="Barbell Squat",
                description="A compound lower-body strength exercise.",
                category=ExerciseCategory.STRENGTH,
                equipment="Barbell",
                steps=["Set the bar on your back", "Squat down", "Stand back up"],
                default_sets=3,
                default_reps=10,
                default_weight_kg=60.0,
                muscles=[MuscleTarget(muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)],
            )
        ]
    )


@pytest.fixture
def mock_session() -> AsyncMock:
    return make_mock_session()


@pytest.fixture
def sample_extraction() -> ExtractionResult:
    return make_sample_extraction()
