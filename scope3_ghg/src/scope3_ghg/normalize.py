"""Normalization helpers."""

import re

INVISIBLE_SPACE_RE = re.compile(r"[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]")


def normalize_compact_text(value: object) -> str:
    text = "" if value is None else str(value)
    return INVISIBLE_SPACE_RE.sub("", text).strip()


def normalize_header_name(value: object) -> str:
    return normalize_compact_text(value)


def to_safe_number(value: object) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return 0.0
    if num != num:  # NaN
        return 0.0
    return num
