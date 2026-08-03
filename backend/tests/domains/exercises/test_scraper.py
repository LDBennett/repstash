from unittest.mock import MagicMock, patch

from app.domains.exercises.scraper import scrape_social_url


def _mock_ydl(info: dict) -> MagicMock:
    ydl_instance = MagicMock()
    ydl_instance.extract_info.return_value = info
    ydl_instance.__enter__.return_value = ydl_instance
    ydl_instance.__exit__.return_value = False
    return ydl_instance


async def test_scrape_uses_description_when_present():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_cls.return_value = _mock_ydl({"description": "Do 3 sets of squats", "title": "Leg day"})

        result = await scrape_social_url("https://example.com/video")

        assert result.caption == "Do 3 sets of squats"


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


async def test_scrape_returns_error_caption_on_exception_instead_of_raising():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_cls:
        ydl_instance = MagicMock()
        ydl_instance.extract_info.side_effect = RuntimeError("blocked by anti-bot")
        ydl_instance.__enter__.return_value = ydl_instance
        ydl_instance.__exit__.return_value = False
        mock_ydl_cls.return_value = ydl_instance

        result = await scrape_social_url("https://example.com/video")

        assert "Failed to scrape URL" in result.caption
        assert "blocked by anti-bot" in result.caption
