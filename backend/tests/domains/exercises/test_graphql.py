from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domains.exercises.graphql import ExerciseMutation, ExerciseQuery
from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole


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


def _info(user=None, session=None) -> SimpleNamespace:
    context = {}
    if user is not None:
        context["user"] = user
    if session is not None:
        context["session"] = session
    return SimpleNamespace(context=context)


async def test_my_exercises_without_user_in_context_raises():
    with pytest.raises(Exception, match="Unauthorized"):
        await ExerciseQuery().my_exercises(_info())


async def test_my_exercises_maps_rows_to_exercise_type(mock_session):
    exercise_row = _make_exercise_row(exercise_id=10, user_id=5)
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[exercise_row])))
    )
    info = _info(user=SimpleNamespace(id=5), session=mock_session)

    result = await ExerciseQuery().my_exercises(info)

    assert len(result) == 1
    exercise_type = result[0]
    assert exercise_type.id == 10
    assert exercise_type.title == "Barbell Squat"
    assert len(exercise_type.muscles) == 1
    assert exercise_type.muscles[0].muscle == MuscleName.QUADRICEPS


async def test_exercise_without_user_in_context_raises():
    with pytest.raises(Exception, match="Unauthorized"):
        await ExerciseQuery().exercise(_info(), id=10)


async def test_exercise_returns_owned_exercise(mock_session):
    exercise_row = _make_exercise_row(exercise_id=10, user_id=5)
    mock_session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=exercise_row)
    )
    info = _info(user=SimpleNamespace(id=5), session=mock_session)

    result = await ExerciseQuery().exercise(info, id=10)

    assert result.id == 10
    assert result.title == "Barbell Squat"


async def test_exercise_not_owned_or_missing_raises_generic_not_found(mock_session):
    # The query filters by id AND user_id, so a row belonging to someone else
    # (or a nonexistent id) both surface as scalar_one_or_none() -> None.
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    info = _info(user=SimpleNamespace(id=5), session=mock_session)

    with pytest.raises(Exception, match="Exercise not found"):
        await ExerciseQuery().exercise(info, id=999)


async def test_update_exercise_without_user_in_context_raises():
    with pytest.raises(Exception, match="Unauthorized"):
        await ExerciseMutation().update_exercise(_info(), id=10, description="new desc")


async def test_update_exercise_updates_owned_exercise(mock_session):
    exercise_row = _make_exercise_row(exercise_id=10, user_id=5)
    mock_session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=exercise_row)
    )
    info = _info(user=SimpleNamespace(id=5), session=mock_session)

    result = await ExerciseMutation().update_exercise(
        info, id=10, description="Updated description", steps=["A", "B"]
    )

    assert exercise_row.description == "Updated description"
    assert exercise_row.steps == ["A", "B"]
    mock_session.commit.assert_called_once()
    assert result.id == 10


async def test_update_exercise_not_owned_or_missing_raises_generic_not_found(mock_session):
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    info = _info(user=SimpleNamespace(id=5), session=mock_session)

    with pytest.raises(Exception, match="Exercise not found"):
        await ExerciseMutation().update_exercise(info, id=999, description="hack")

    mock_session.commit.assert_not_called()
