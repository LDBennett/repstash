from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from app.domains.exercises.ai_extractor import extract_exercises_from_content

SAMPLE_JSON = (
    '{"title": "Push Up", "description": null, "category": "STRENGTH", '
    '"equipment": null, "steps": ["Step 1", "Step 2"], "default_sets": null, '
    '"default_reps": null, "default_weight_kg": null, "muscles": []}'
)


def _mock_client_with_response(text: str) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.text = text
    client.models.generate_content.return_value = response
    return client


async def test_no_video_bytes_skips_upload_and_parses_result():
    client = _mock_client_with_response(SAMPLE_JSON)

    with patch("app.domains.exercises.ai_extractor.client", client):
        result = await extract_exercises_from_content(caption="Some caption")

    client.files.upload.assert_not_called()
    client.files.delete.assert_not_called()
    _, kwargs = client.models.generate_content.call_args
    assert len(kwargs["contents"]) == 1
    assert result.title == "Push Up"


async def test_video_bytes_uploads_and_cleans_up():
    client = _mock_client_with_response(SAMPLE_JSON)
    uploaded_file = MagicMock()
    uploaded_file.name = "files/abc123"
    client.files.upload.return_value = uploaded_file

    video_bytes = BytesIO(b"fake video data")

    with patch("app.domains.exercises.ai_extractor.client", client):
        await extract_exercises_from_content(
            caption="Some caption", video_bytes=video_bytes, mime_type="video/mp4"
        )

    client.files.upload.assert_called_once_with(file=video_bytes, config={"mime_type": "video/mp4"})
    _, kwargs = client.models.generate_content.call_args
    assert uploaded_file in kwargs["contents"]
    client.files.delete.assert_called_once_with(name="files/abc123")
    assert video_bytes.closed


async def test_empty_response_text_raises_value_error_and_still_cleans_up():
    client = _mock_client_with_response("")
    uploaded_file = MagicMock()
    uploaded_file.name = "files/abc123"
    client.files.upload.return_value = uploaded_file

    video_bytes = BytesIO(b"fake video data")

    with patch("app.domains.exercises.ai_extractor.client", client):
        with pytest.raises(ValueError, match="empty response"):
            await extract_exercises_from_content(
                caption="Some caption", video_bytes=video_bytes, mime_type="video/mp4"
            )

    client.files.delete.assert_called_once_with(name="files/abc123")
    assert video_bytes.closed


async def test_uploaded_file_without_name_skips_delete():
    client = _mock_client_with_response(SAMPLE_JSON)
    uploaded_file = MagicMock()
    uploaded_file.name = None
    client.files.upload.return_value = uploaded_file

    video_bytes = BytesIO(b"fake video data")

    with patch("app.domains.exercises.ai_extractor.client", client):
        await extract_exercises_from_content(
            caption="Some caption", video_bytes=video_bytes, mime_type="video/mp4"
        )

    client.files.delete.assert_not_called()
    assert video_bytes.closed


async def test_cleanup_still_runs_when_generate_content_raises():
    client = MagicMock()
    uploaded_file = MagicMock()
    uploaded_file.name = "files/abc123"
    client.files.upload.return_value = uploaded_file
    client.models.generate_content.side_effect = RuntimeError("gemini is down")

    video_bytes = BytesIO(b"fake video data")

    with patch("app.domains.exercises.ai_extractor.client", client):
        with pytest.raises(RuntimeError, match="gemini is down"):
            await extract_exercises_from_content(
                caption="Some caption", video_bytes=video_bytes, mime_type="video/mp4"
            )

    client.files.delete.assert_called_once_with(name="files/abc123")
    assert video_bytes.closed
