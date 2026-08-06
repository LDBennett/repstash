from io import BytesIO
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

class ScrapeResult:
    def __init__(self, caption: str, video_bytes: BytesIO | None = None, mime_type: str = "video/mp4", thumbnail_url: str | None = None):
        self.caption = caption
        self.video_bytes = video_bytes
        self.mime_type = mime_type
        self.thumbnail_url = thumbnail_url


async def _download_video(info: dict) -> BytesIO | None:
    """Best-effort download of the video yt-dlp resolved in `info`. Never raises —
    any failure here (network error, anti-bot block, oversized file) just means
    the import falls back to caption-only extraction."""
    duration = info.get('duration')
    if duration is None or duration > settings.MAX_VIDEO_DURATION_SECONDS:
        return None

    ext = info.get('ext')
    direct_url = info.get('url')
    if ext != 'mp4' or not direct_url:
        return None

    known_size = info.get('filesize') or info.get('filesize_approx')
    if known_size and known_size > settings.MAX_VIDEO_DOWNLOAD_BYTES:
        logger.warning(f"Skipping video download, reported size {known_size} exceeds cap")
        return None

    headers = info.get('http_headers') or {}

    try:
        buffer = BytesIO()
        total = 0
        async with httpx.AsyncClient(timeout=settings.VIDEO_DOWNLOAD_TIMEOUT_SECONDS) as client:
            async with client.stream("GET", direct_url, headers=headers) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > settings.MAX_VIDEO_DOWNLOAD_BYTES:
                        logger.warning("Aborting video download, exceeded size cap mid-stream")
                        return None
                    buffer.write(chunk)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.warning(f"Video download failed, falling back to caption-only: {e}")
        return None


async def scrape_social_url(url: str) -> ScrapeResult:
    """
    Scrapes a social media URL for its caption/thumbnail metadata (via yt-dlp),
    and best-effort downloads the underlying video for richer AI extraction.

    In a production app, metadata extraction would use a more robust scraping
    API (e.g. Apify, RapidAPI, or custom playwright) to bypass anti-bot
    mechanisms; yt-dlp is used here as a pragmatic starting point.
    """

    logger.info(f"Attempting to scrape URL: {url}")

    import yt_dlp

    # Resolve metadata and a downloadable format URL, but don't let yt-dlp
    # itself download the file — that's handled separately via httpx so we
    # can stream into memory with a size cap.
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',
    }

    # yt-dlp's typeshed stub mistypes skip_download as str | None; it's actually a bool flag at runtime
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
        info = ydl.extract_info(url, download=False)

    caption = info.get('description', '') or info.get('title', '')
    thumbnail_url = info.get('thumbnail')
    if not caption:
        caption = "Could not extract a caption from this link."

    video_bytes = await _download_video(info)

    return ScrapeResult(
        caption=caption,
        video_bytes=video_bytes,
        mime_type="video/mp4",
        thumbnail_url=thumbnail_url,
    )
