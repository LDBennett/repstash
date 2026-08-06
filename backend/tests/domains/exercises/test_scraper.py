from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.domains.exercises.scraper import scrape_social_url


def _mock_ydl(info: dict) -> MagicMock:
    ydl_instance = MagicMock()
    ydl_instance.extract_info.return_value = info
    ydl_instance.__enter__.return_value = ydl_instance
    ydl_instance.__exit__.return_value = False
    return ydl_instance


def _mock_httpx_client_cls(chunks: list[bytes] | None = None, enter_error: Exception | None = None, status_error: Exception | None = None) -> MagicMock:
    """Stands in for `async with httpx.AsyncClient(...) as client:
    async with client.stream(...) as response: ...`"""

    async def aiter_bytes():
        for chunk in chunks or []:
            yield chunk

    response = MagicMock()
    response.raise_for_status = MagicMock(side_effect=status_error)
    response.aiter_bytes = aiter_bytes

    stream_cm = MagicMock()
    stream_cm.__aenter__ = AsyncMock(side_effect=enter_error) if enter_error else AsyncMock(return_value=response)
    stream_cm.__aexit__ = AsyncMock(return_value=False)

    client = MagicMock()
    client.stream = MagicMock(return_value=stream_cm)

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client)
    client_cm.__aexit__ = AsyncMock(return_value=False)

    return MagicMock(return_value=client_cm)


async def test_scrape_uses_description_when_present():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_cls.return_value = _mock_ydl({"description": "Do 3 sets of squats", "title": "Leg day"})

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Do 3 sets of squats"
        assert result.video_bytes is None


async def test_scrape_falls_back_to_title_when_no_description():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_cls.return_value = _mock_ydl({"description": "", "title": "Leg day"})

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Leg day"


async def test_scrape_falls_back_to_placeholder_when_both_empty():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_cls.return_value = _mock_ydl({"description": "", "title": ""})

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Could not extract a caption from this link."


async def test_scrape_raises_when_metadata_extraction_fails():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        ydl_instance = MagicMock()
        ydl_instance.extract_info.side_effect = RuntimeError("blocked by anti-bot")
        ydl_instance.__enter__.return_value = ydl_instance
        ydl_instance.__exit__.return_value = False
        mock_ydl_cls.return_value = ydl_instance

        with pytest.raises(RuntimeError, match="blocked by anti-bot"):
            await scrape_social_url("https://example.com/video")


async def test_scrape_skips_download_when_duration_exceeds_cap():
    info = {"description": "Long video", "duration": 10_000}
    with (
        patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
        patch("app.domains.exercises.scraper.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_ydl_cls.return_value = _mock_ydl(info)

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Long video"
        assert result.video_bytes is None
        mock_client_cls.assert_not_called()


async def test_scrape_skips_download_when_format_is_not_mp4():
    info = {"description": "Webm video", "duration": 30, "ext": "webm", "url": "https://cdn.example.com/v.webm"}
    with (
        patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
        patch("app.domains.exercises.scraper.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_ydl_cls.return_value = _mock_ydl(info)

        result = await scrape_social_url("https://example.com/video")

        assert result.video_bytes is None
        mock_client_cls.assert_not_called()


async def test_scrape_downloads_video_bytes_on_success():
    info = {
        "description": "Do 3 sets of squats",
        "duration": 30,
        "ext": "mp4",
        "url": "https://cdn.example.com/v.mp4",
        "thumbnail": "https://cdn.example.com/thumb.jpg",
    }
    with (
        patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
        patch(
            "app.domains.exercises.scraper.httpx.AsyncClient",
            _mock_httpx_client_cls(chunks=[b"abc", b"def"]),
        ),
    ):
        mock_ydl_cls.return_value = _mock_ydl(info)

        result = await scrape_social_url("https://example.com/video")

        assert result.video_bytes is not None
        assert result.video_bytes.read() == b"abcdef"
        assert result.mime_type == "video/mp4"
        assert result.thumbnail_url == "https://cdn.example.com/thumb.jpg"


async def test_scrape_aborts_download_when_size_cap_exceeded_mid_stream():
    info = {"description": "Big video", "duration": 30, "ext": "mp4", "url": "https://cdn.example.com/v.mp4"}
    with (
        patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
        patch("app.domains.exercises.scraper.settings.MAX_VIDEO_DOWNLOAD_BYTES", 10),
        patch(
            "app.domains.exercises.scraper.httpx.AsyncClient",
            _mock_httpx_client_cls(chunks=[b"01234567", b"89ABCDEF"]),  # 16 bytes > 10-byte cap
        ),
    ):
        mock_ydl_cls.return_value = _mock_ydl(info)

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Big video"
        assert result.video_bytes is None


async def test_scrape_falls_back_to_caption_only_when_download_raises():
    info = {"description": "Flaky CDN", "duration": 30, "ext": "mp4", "url": "https://cdn.example.com/v.mp4"}
    with (
        patch("yt_dlp.YoutubeDL") as mock_ydl_cls,
        patch(
            "app.domains.exercises.scraper.httpx.AsyncClient",
            _mock_httpx_client_cls(enter_error=httpx.ConnectError("connection reset")),
        ),
    ):
        mock_ydl_cls.return_value = _mock_ydl(info)

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Flaky CDN"
        assert result.video_bytes is None
