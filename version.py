"""Single source of truth for RecipeScope version metadata."""

from __future__ import annotations

APP_NAME = "RecipeScope"
VERSION = "2026.11.0"
VERSION_TUPLE = (2026, 11, 0)
RELEASE_DATE = "2026-11-17"
COMPANY_NAME = "ASM"
DEPARTMENT_NAME = "RF Engineering"
AUTHOR_NAME = "Victor Huang"
AUTHOR_EMAIL = "victor.huang@asm.com"


def get_version() -> str:
    return VERSION


def get_version_tuple() -> tuple[int, int, int]:
    return VERSION_TUPLE


def get_display_name() -> str:
    return f"{APP_NAME} v{VERSION}"


def get_executable_name() -> str:
    return f"{APP_NAME}_v{VERSION}.exe"
