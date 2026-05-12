"""data.py — Re-exports all static data and helpers from the legacy app module.

During the blueprint migration, this shim lets blueprints import data without
duplicating the ~1400 lines of seed data. Once app.py is fully retired, move
the data constants here directly.
"""
# ruff: noqa: F401  (re-exports are intentional)
import sys, os

# Ensure the project root is on sys.path so we can import app.py
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from app import (  # noqa: E402
    SKILL_RECOMMENDATIONS,
    SKILL_PATHS,
    SUPPORTED_LANGUAGES,
    I18N,
    PATH_NOTES,
    SUBTITLE_LANGS,
    NEXT_STEP_MSG,
    COURSE_NOTES,
    get_videos_for_course,
)
