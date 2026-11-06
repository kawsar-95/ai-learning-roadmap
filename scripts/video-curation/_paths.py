"""Where the curation scripts keep their files. Imported by every script in this folder.

VIDEO_WORK   a directory for crawl lists, caches and lookups (default: <temp dir>/video-curation). Nothing here is committed.
YT_DLP       the yt-dlp binary (default: yt-dlp on PATH).
"""
import os
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]
WORK = Path(os.environ.get("VIDEO_WORK") or Path(tempfile.gettempdir()) / "video-curation")
WORK.mkdir(parents=True, exist_ok=True)
YT_DLP = os.environ.get("YT_DLP", "yt-dlp")
