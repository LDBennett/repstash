from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.domains.imports.graphql as graphql_module
from app.domains.imports.models import JobStatus
from tests.conftest import FakeAsyncSessionCM as _FakeSessionCM


async def test_import_exercise_creates_job_and_enqueues_task(mock_session):
    async def fake_refresh(obj):
        obj.id = 123

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    mock_redis = AsyncMock()

    class MockUser:
        id = 7

    mock_info = MagicMock()
    mock_info.context = {"user": MockUser()}

    with (
        patch("app.domains.imports.graphql.AsyncSessionLocal", lambda: _FakeSessionCM(mock_session)),
        patch("app.domains.imports.graphql.get_redis_pool", AsyncMock(return_value=mock_redis)),
    ):
        mutation = graphql_module.ImportMutation()
        result = await mutation.import_exercise(info=mock_info, url="https://example.com/reel")

    added_job = mock_session.add.call_args.args[0]
    assert added_job.status == JobStatus.PENDING
    assert added_job.user_id == 7
    assert added_job.source_url == "https://example.com/reel"

    mock_session.commit.assert_called_once()
    mock_redis.enqueue_job.assert_called_once_with("import_url_task", 123, "https://example.com/reel", 7)

    assert result.id == 123
    assert result.status == JobStatus.PENDING


async def test_import_exercise_rejects_missing_user(mock_session):
    mock_info = MagicMock()
    mock_info.context = {"user": None}

    with (
        patch("app.domains.imports.graphql.AsyncSessionLocal", lambda: _FakeSessionCM(mock_session)),
    ):
        mutation = graphql_module.ImportMutation()
        with pytest.raises(Exception, match="Unauthorized"):
            await mutation.import_exercise(info=mock_info, url="https://example.com/reel")

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


async def test_get_redis_pool_caches_the_pool():
    graphql_module._redis_pool = None
    fake_pool = object()

    try:
        with patch(
            "app.domains.imports.graphql.create_pool", AsyncMock(return_value=fake_pool)
        ) as mock_create_pool:
            first = await graphql_module.get_redis_pool()
            second = await graphql_module.get_redis_pool()

        assert first is fake_pool
        assert second is fake_pool
        mock_create_pool.assert_called_once()
    finally:
        graphql_module._redis_pool = None
