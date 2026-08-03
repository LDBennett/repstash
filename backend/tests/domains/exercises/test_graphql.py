from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.domains.exercises.graphql import ExerciseQuery
from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole
from tests.conftest import FakeAsyncSessionCM


def _make_exercise_row(exercise_id: int, user_id: int) -> SimpleNamespace:
    muscle_row = SimpleNamespace(id=1, muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)
    return SimpleNamespace(
        id=exercise_id,
        user_id=user_id,
        title="Barbell Squat",
        description=None,
        category=ExerciseCategory.STRENGTH,
        equipment=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        steps=["Set up", "Squat", "Stand"],
        default_sets=3,
        default_reps=10,
        default_weight_kg=60.0,
        source_url=None,
        muscles=[muscle_row],
    )


async def test_my_exercises_without_user_in_context_raises():
    info = SimpleNamespace(context={})

    with pytest.raises(Exception, match="Unauthorized"):
        await ExerciseQuery().my_exercises(info)


async def test_my_exercises_maps_rows_to_exercise_type(mock_session):
    exercise_row = _make_exercise_row(exercise_id=10, user_id=5)
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[exercise_row])))
    )
    info = SimpleNamespace(context={"user": SimpleNamespace(id=5)})

    with patch("app.domains.exercises.graphql.AsyncSessionLocal", lambda: FakeAsyncSessionCM(mock_session)):
        result = await ExerciseQuery().my_exercises(info)

    assert len(result) == 1
    exercise_type = result[0]
    assert exercise_type.id == 10
    assert exercise_type.title == "Barbell Squat"
    assert len(exercise_type.muscles) == 1
    assert exercise_type.muscles[0].muscle == MuscleName.QUADRICEPS
