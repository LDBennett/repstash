from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.domains.exercises.models import ExerciseCategory, MuscleName, MuscleRole
from app.domains.exercises.schemas import (
    ExerciseExtraction,
    ExerciseMuscleRead,
    ExerciseRead,
    ExtractionResult,
    MuscleTarget,
)


def test_optional_fields_default_and_muscles_defaults_to_empty_list():
    extraction = ExerciseExtraction(
        title="Push Up",
        category=ExerciseCategory.STRENGTH,
        steps=["Get into plank", "Lower", "Push up"],
    )

    assert extraction.description is None
    assert extraction.equipment is None
    assert extraction.default_sets is None
    assert extraction.default_reps is None
    assert extraction.default_weight_kg is None
    assert extraction.muscles == []


@pytest.mark.parametrize("missing_field", ["title", "category", "steps"])
def test_required_fields_raise_when_missing(missing_field):
    fields = {
        "title": "Push Up",
        "category": ExerciseCategory.STRENGTH,
        "steps": ["Get into plank"],
    }
    del fields[missing_field]

    with pytest.raises(ValidationError):
        ExerciseExtraction(**fields)


def test_invalid_category_raises_validation_error():
    with pytest.raises(ValidationError):
        ExerciseExtraction(title="Push Up", category="NOT_A_REAL_CATEGORY", steps=["Do it"])


def test_extraction_result_round_trips_through_json():
    original = ExtractionResult(
        exercises=[
            ExerciseExtraction(
                title="Barbell Squat",
                category=ExerciseCategory.STRENGTH,
                steps=["Set up", "Squat", "Stand"],
                muscles=[MuscleTarget(muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)],
            )
        ]
    )

    round_tripped = ExtractionResult.model_validate_json(original.model_dump_json())

    assert round_tripped == original


def test_exercise_read_validates_from_orm_style_object():
    muscle_row = SimpleNamespace(id=1, muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)
    exercise_row = SimpleNamespace(
        id=10,
        user_id=5,
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

    read = ExerciseRead.model_validate(exercise_row)

    assert read.id == 10
    assert read.title == "Barbell Squat"
    assert read.muscles == [ExerciseMuscleRead(id=1, muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)]
