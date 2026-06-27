from __future__ import annotations

import re
import unicodedata


_whitespace_re = re.compile(r"\s+")
_non_printable_re = re.compile(r"[\x00-\x1F\x7F]")


def normalize_text(text: str) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\n", " ").replace("\r", " ").strip()
    normalized = _non_printable_re.sub(" ", normalized)
    normalized = _whitespace_re.sub(" ", normalized)
    return normalized


def lowercase_text(text: str) -> str:
    return normalize_text(text).lower()