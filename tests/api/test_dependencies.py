from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.dependencies import get_current_user
from tests.conftest import FakeAsyncSessionCM


def _make_request(auth_header: str | None) -> MagicMock:
    request = MagicMock()
    request.headers = {"Authorization": auth_header} if auth_header else {}
    return request


def _make_request_state(is_signed_in: bool, payload: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(is_signed_in=is_signed_in, payload=payload or {})


async def test_no_authorization_header_returns_none_without_calling_clerk():
    request = _make_request(None)

    with patch("app.api.dependencies.clerk_client") as mock_clerk:
        user = await get_current_user(request)

    assert user is None
    mock_clerk.authenticate_request.assert_not_called()


async def test_non_bearer_header_returns_none():
    request = _make_request("Basic abc123")

    with patch("app.api.dependencies.clerk_client") as mock_clerk:
        user = await get_current_user(request)

    assert user is None
    mock_clerk.authenticate_request.assert_not_called()


async def test_valid_token_for_existing_user_returns_that_user(mock_session):
    request = _make_request("Bearer valid-token")
    existing_user = SimpleNamespace(id=1, clerk_id="clerk_123", email="a@b.com")
    mock_session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=existing_user)
    )

    with (
        patch("app.api.dependencies.clerk_client") as mock_clerk,
        patch("app.api.dependencies.AsyncSessionLocal", lambda: FakeAsyncSessionCM(mock_session)),
    ):
        mock_clerk.authenticate_request.return_value = _make_request_state(
            is_signed_in=True, payload={"sub": "clerk_123"}
        )
        user = await get_current_user(request)

    assert user is existing_user
    mock_session.add.assert_not_called()


async def test_valid_token_for_new_user_auto_provisions(mock_session):
    request = _make_request("Bearer valid-token")
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    async def fake_refresh(obj):
        obj.id = 99

    mock_session.refresh.side_effect = fake_refresh

    with (
        patch("app.api.dependencies.clerk_client") as mock_clerk,
        patch("app.api.dependencies.AsyncSessionLocal", lambda: FakeAsyncSessionCM(mock_session)),
    ):
        mock_clerk.authenticate_request.return_value = _make_request_state(
            is_signed_in=True, payload={"sub": "clerk_new", "email": "new@example.com"}
        )
        user = await get_current_user(request)

    created_user = mock_session.add.call_args.args[0]
    assert created_user.clerk_id == "clerk_new"
    assert created_user.email == "new@example.com"
    mock_session.commit.assert_called_once()
    assert user is created_user
    assert user.id == 99


async def test_new_user_without_email_claim_gets_placeholder_email(mock_session):
    request = _make_request("Bearer valid-token")
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with (
        patch("app.api.dependencies.clerk_client") as mock_clerk,
        patch("app.api.dependencies.AsyncSessionLocal", lambda: FakeAsyncSessionCM(mock_session)),
    ):
        mock_clerk.authenticate_request.return_value = _make_request_state(
            is_signed_in=True, payload={"sub": "clerk_new"}
        )
        await get_current_user(request)

    created_user = mock_session.add.call_args.args[0]
    assert created_user.email == "clerk_new@placeholder.com"


async def test_not_signed_in_raises_401():
    request = _make_request("Bearer expired-token")

    with patch("app.api.dependencies.clerk_client") as mock_clerk:
        mock_clerk.authenticate_request.return_value = _make_request_state(is_signed_in=False)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired auth token"


async def test_clerk_sdk_error_raises_401():
    request = _make_request("Bearer bad-token")

    with patch("app.api.dependencies.clerk_client") as mock_clerk:
        mock_clerk.authenticate_request.side_effect = RuntimeError("clerk is unreachable")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)

    assert exc_info.value.status_code == 401
    assert "clerk is unreachable" in exc_info.value.detail
