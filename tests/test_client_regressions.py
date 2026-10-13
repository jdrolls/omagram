from __future__ import annotations

import asyncio
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from PIL import Image
from telethon.tl import types

from telegram_tui.client import TelegramBackend, YOUTUBE_ID_RE, YOUTUBE_RE


def make_backend(cache_dir: str, session_dir: str) -> TelegramBackend:
    with patch.dict("os.environ", {"XDG_CACHE_HOME": cache_dir}):
        return TelegramBackend(1, "hash", str(Path(session_dir) / "session"))


def close_backend(backend: TelegramBackend) -> None:
    backend.client.session.close()


def create_dummy_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with Image.new("RGB", (32, 32), color="blue") as img:
        img.save(path, format="JPEG")


class YoutubeRegexTests(unittest.TestCase):
    def test_youtube_watch_url_with_preceding_query_params(self):
        url = "https://youtube.com/watch?list=PL123&v=dQw4w9WgXcQ"
        match = YOUTUBE_RE.search(url)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(0), url)
        id_match = YOUTUBE_ID_RE.search(url)
        self.assertIsNotNone(id_match)
        self.assertEqual(id_match.group(1).split("&", 1)[0], "dQw4w9WgXcQ")

    def test_youtube_watch_url_with_multiple_params(self):
        url = "https://www.youtube.com/watch?feature=shared&list=PL123&v=dQw4w9WgXcQ&t=10s"
        match = YOUTUBE_RE.search(url)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(0), url)
        id_match = YOUTUBE_ID_RE.search(url)
        self.assertIsNotNone(id_match)
        self.assertEqual(id_match.group(1).split("&", 1)[0], "dQw4w9WgXcQ")

    def test_youtube_watch_url_standard(self):
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        match = YOUTUBE_RE.search(url)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(0), url)

    def test_youtube_short_and_youtu_be_urls(self):
        for url in [
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ]:
            match = YOUTUBE_RE.search(url)
            self.assertIsNotNone(match, f"Failed to match: {url}")
            id_match = YOUTUBE_ID_RE.search(url)
            self.assertIsNotNone(id_match)
            self.assertEqual(id_match.group(1).split("&", 1)[0], "dQw4w9WgXcQ")

    def test_youtube_watch_without_v_does_not_match(self):
        url = "https://youtube.com/watch?list=PL123&index=1"
        match = YOUTUBE_RE.search(url)
        self.assertIsNone(match)


class VideoThumbnailSelectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_video_thumbnail_prefers_static_photo_over_video_size(self):
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as session_dir:
            backend = make_backend(cache_dir, session_dir)
            small_photo = types.PhotoSize("s", 90, 90, 500)
            large_photo = types.PhotoSize("m", 180, 180, 4000)
            video_thumb = types.VideoSize("u", 100, 100, 5000, 0)
            doc = SimpleNamespace(
                id=10,
                mime_type="video/mp4",
                thumbs=[small_photo, video_thumb, large_photo],
            )
            item = SimpleNamespace(
                id=42,
                photo=None,
                gif=None,
                video=doc,
                document=doc,
                media=types.MessageMediaDocument(document=doc),
            )

            async def fake_download(target_item, file=None, thumb=None, **kwargs):
                self.assertEqual(thumb, "m")
                create_dummy_image(Path(file))
                return file

            backend.client.download_media = AsyncMock(side_effect=fake_download)
            try:
                result = await backend._cache_media_thumbnail(1, item)
                self.assertIsNotNone(result)
                self.assertTrue(result.is_file())
                self.assertEqual(result.name, "42.jpg")
                backend.client.download_media.assert_awaited_once()
            finally:
                close_backend(backend)

    async def test_video_thumbnail_skips_download_when_no_static_preview_exists(self):
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as session_dir:
            backend = make_backend(cache_dir, session_dir)
            video_thumb = types.VideoSize("u", 100, 100, 5000, 0)
            doc = SimpleNamespace(
                id=11,
                mime_type="video/mp4",
                thumbs=[video_thumb],
            )
            item = SimpleNamespace(
                id=43,
                photo=None,
                gif=None,
                video=doc,
                document=doc,
                media=types.MessageMediaDocument(document=doc),
            )
            backend.client.download_media = AsyncMock()
            try:
                result = await backend._cache_media_thumbnail(1, item)
                self.assertIsNone(result)
                backend.client.download_media.assert_not_awaited()
            finally:
                close_backend(backend)


class OrphanedTempFilesCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_download_media_cleans_orphaned_temps_for_message(self):
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as session_dir:
            backend = make_backend(cache_dir, session_dir)
            dialog_dir = Path(cache_dir) / "omagram" / "media" / "1"
            dialog_dir.mkdir(parents=True, exist_ok=True)

            orphaned_file = dialog_dir / ".100.tmp-deadbeef1234.mp4"
            orphaned_file.write_bytes(b"old partial data")
            other_message_temp = dialog_dir / ".200.tmp-deadbeef5678.mp4"
            other_message_temp.write_bytes(b"leave me alone")

            item = SimpleNamespace(
                id=100,
                file=SimpleNamespace(size=10, ext=".mp4"),
                photo=None,
                gif=None,
                video=SimpleNamespace(),
                document=SimpleNamespace(),
                media=None,
            )

            async def fake_download(target_item, file=None, **kwargs):
                Path(file).write_bytes(b"completed video")
                return file

            backend.client.download_media = AsyncMock(side_effect=fake_download)
            try:
                result = await backend._cache_media(1, item)
                self.assertIsNotNone(result)
                self.assertFalse(orphaned_file.exists())
                self.assertTrue(other_message_temp.exists())
            finally:
                close_backend(backend)

    async def test_cache_media_thumbnail_cleans_orphaned_temps_for_message(self):
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as session_dir:
            backend = make_backend(cache_dir, session_dir)
            thumbs_dir = Path(cache_dir) / "omagram" / "media" / "1" / "thumbs"
            thumbs_dir.mkdir(parents=True, exist_ok=True)

            orphaned_jpg = thumbs_dir / ".101.tmp-abc123.jpg"
            orphaned_jpg.write_bytes(b"corrupt")
            orphaned_mp4 = thumbs_dir / ".101.tmp-abc123.mp4"
            orphaned_mp4.write_bytes(b"old video thumb")
            other_temp = thumbs_dir / ".201.tmp-xyz789.jpg"
            other_temp.write_bytes(b"other")

            photo_thumb = types.PhotoSize("s", 90, 90, 500)
            item = SimpleNamespace(
                id=101,
                photo=None,
                gif=None,
                video=SimpleNamespace(thumbs=[photo_thumb]),
                document=SimpleNamespace(thumbs=[photo_thumb]),
                media=None,
            )

            async def fake_download(target_item, file=None, **kwargs):
                create_dummy_image(Path(file))
                return file

            backend.client.download_media = AsyncMock(side_effect=fake_download)
            try:
                result = await backend._cache_media_thumbnail(1, item)
                self.assertIsNotNone(result)
                self.assertFalse(orphaned_jpg.exists())
                self.assertFalse(orphaned_mp4.exists())
                self.assertTrue(other_temp.exists())
            finally:
                close_backend(backend)

    async def test_cache_gif_thumbnail_cleans_orphaned_temps_and_fallbacks(self):
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as session_dir:
            backend = make_backend(cache_dir, session_dir)
            thumbs_dir = Path(cache_dir) / "omagram" / "media" / "1" / "thumbs"
            thumbs_dir.mkdir(parents=True, exist_ok=True)

            orphaned_fallback = thumbs_dir / ".102.fallback-old123.jpg"
            orphaned_fallback.write_bytes(b"incomplete")
            orphaned_tmp = thumbs_dir / ".102.tmp-old456.jpg"
            orphaned_tmp.write_bytes(b"incomplete")
            other_fallback = thumbs_dir / ".202.fallback-keep.jpg"
            other_fallback.write_bytes(b"keep")

            photo_thumb = types.PhotoSize("s", 90, 90, 500)
            doc = SimpleNamespace(
                id=12,
                mime_type="image/gif",
                thumbs=[photo_thumb],
            )
            item = SimpleNamespace(
                id=102,
                photo=None,
                gif=doc,
                video=None,
                document=doc,
                media=types.MessageMediaDocument(document=doc),
            )

            async def fake_download(target_item, file=None, **kwargs):
                create_dummy_image(Path(file))
                return file

            backend.client.download_media = AsyncMock(side_effect=fake_download)
            try:
                result = await backend._cache_gif_thumbnail(1, item)
                self.assertIsNotNone(result)
                self.assertFalse(orphaned_fallback.exists())
                self.assertFalse(orphaned_tmp.exists())
                self.assertTrue(other_fallback.exists())
            finally:
                close_backend(backend)


if __name__ == "__main__":
    unittest.main()
