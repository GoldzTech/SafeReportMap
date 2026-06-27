from __future__ import annotations

import re


_sentence_splitter = re.compile(r"(?<=[.!?])\s+")


def generate_summary(text: str, max_length: int = 220) -> str:
    clean = text.strip()
    if not clean:
        return "Relato sem conteúdo textual suficiente para resumo."

    sentences = _sentence_splitter.split(clean)
    candidate = sentences[0] if sentences else clean

    if len(candidate) <= max_length:
        return candidate

    return candidate[: max_length - 3].rstrip() + "..."