from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.domains.exercises.models import Exercise, MuscleName, MuscleRole
from app.domains.exercises.scraper import ScrapeResult
from app.domains.imports.models import ImportJob, ImportLog, JobStatus
from app.domains.imports.service import process_import_job


def _assign_ids_on_flush(mock_session, start: int = 1) -> None:
    """The real `session.flush()` assigns DB-generated PKs; the mock doesn't.
    Simulate that so assertions on `job.exercise_id` are meaningful instead
    of trivially comparing None to None."""
    counter = iter(range(start, start + 1000))

    async def fake_flush():
        added_obj = mock_session.add.call_args.args[0]
        if isinstance(added_obj, Exercise) and added_obj.id is None:
            added_obj.id = next(counter)

    mock_session.flush.side_effect = fake_flush


async def test_job_not_found_returns_early(mock_session):
    mock_session.get.return_value = None

    await process_import_job(mock_session, job_id=1, source_url="https://example.com", user_id=1)

    mock_session.commit.assert_not_called()
    mock_session.add.assert_not_called()


async def test_happy_path_completes_job_and_persists_exercises(mock_session, sample_extraction):
    job = ImportJob(id=1, user_id=1, source_url="https://example.com", status=JobStatus.PENDING)
    mock_session.get.return_value = job
    _assign_ids_on_flush(mock_session)

    scrape_result = ScrapeResult(caption="do 3 sets of squats")

    with (
        patch("app.domains.imports.service.scrape_social_url", AsyncMock(return_value=scrape_result)),
        patch(
            "app.domains.imports.service.extract_exercises_from_content",
            AsyncMock(return_value=sample_extraction),
        ),
    ):
        await process_import_job(mock_session, job_id=1, source_url="https://example.com", user_id=42)

    assert job.status == JobStatus.COMPLETED

    added = [call.args[0] for call in mock_session.add.call_args_list]
    added_by_type = {type(obj).__name__: obj for obj in added}
    assert set(added_by_type) == {"ImportLog", "Exercise", "ExerciseMuscle"}

    added_log = added_by_type["ImportLog"]
    assert added_log.status == JobStatus.COMPLETED
    assert added_log.raw_payload == "do 3 sets of squats"
    assert added_log.llm_prompt_used

    added_exercise = added_by_type["Exercise"]
    assert added_exercise.title == "Barbell Squat"
    assert added_exercise.user_id == 42
    assert added_exercise.source_url == "https://example.com"

    added_muscle = added_by_type["ExerciseMuscle"]
    assert added_muscle.muscle == sample_extraction.muscles[0].muscle
    assert added_muscle.role == sample_extraction.muscles[0].role

    assert job.exercise_id == added_exercise.id


async def test_dedup_path_copies_existing_exercise_and_sets_job_exercise_id(mock_session):
    job = ImportJob(id=1, user_id=1, source_url="https://example.com", status=JobStatus.PENDING)
    mock_session.get.return_value = job
    _assign_ids_on_flush(mock_session)

    muscle_row = SimpleNamespace(muscle=MuscleName.QUADRICEPS, role=MuscleRole.PRIMARY)
    existing_exercise = SimpleNamespace(
        id=10,
        user_id=99,
        title="Barbell Squat",
        description="desc",
        category="STRENGTH",
        equipment=None,
        steps=["Set up", "Squat", "Stand"],
        default_sets=3,
        default_reps=10,
        default_weight_kg=60.0,
        thumbnail_url="https://example.com/thumb.jpg",
        muscles=[muscle_row],
    )
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(
            return_value=MagicMock(unique=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_exercise]))))
        )
    )

    with (
        patch("app.domains.imports.service.scrape_social_url", AsyncMock()) as mock_scrape,
        patch("app.domains.imports.service.extract_exercises_from_content", AsyncMock()) as mock_extract,
    ):
        await process_import_job(mock_session, job_id=1, source_url="https://example.com", user_id=42)

    mock_scrape.assert_not_called()
    mock_extract.assert_not_called()

    added = [call.args[0] for call in mock_session.add.call_args_list]
    added_by_type = {type(obj).__name__: obj for obj in added}
    assert set(added_by_type) == {"ImportLog", "Exercise", "ExerciseMuscle"}

    copied_exercise = added_by_type["Exercise"]
    assert copied_exercise.user_id == 42
    assert copied_exercise.title == "Barbell Squat"
    assert copied_exercise.thumbnail_url == "https://example.com/thumb.jpg"

    assert job.status == JobStatus.COMPLETED
    assert job.exercise_id == copied_exercise.id


async def test_failure_marks_job_and_log_as_failed_with_traceback(mock_session):
    job = ImportJob(id=1, user_id=1, source_url="https://example.com", status=JobStatus.PENDING)
    import_log = ImportLog(id=99, job_id=1, source_url="https://example.com", status=JobStatus.PROCESSING)

    mock_session.get.side_effect = [job, job, import_log]

    with (
        patch(
            "app.domains.imports.service.scrape_social_url",
            AsyncMock(return_value=ScrapeResult(caption="x")),
        ),
        patch(
            "app.domains.imports.service.extract_exercises_from_content",
            AsyncMock(side_effect=RuntimeError("gemini exploded")),
        ),
    ):
        await process_import_job(mock_session, job_id=1, source_url="https://example.com", user_id=1)

    mock_session.rollback.assert_called_once()
    assert job.status == JobStatus.FAILED
    assert import_log.status == JobStatus.FAILED
    assert "gemini exploded" in import_log.error_message
    assert "RuntimeError" in import_log.error_message
