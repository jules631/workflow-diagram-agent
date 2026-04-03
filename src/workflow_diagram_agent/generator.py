from __future__ import annotations

import re
from typing import Iterable

_SMALL_WORDS = {"and", "or", "the", "a", "an", "to", "for", "of", "on", "in", "at", "by", "with"}
_SPLIT_PATTERN = re.compile(r"(?:\r?\n)+|(?<=[.!?])\s+(?=[A-Z0-9])")
_BULLET_PREFIX = re.compile(r"^\s*(?:[-*•]+|\d+[.)])\s*")
_SPACES = re.compile(r"\s+")


def _title_case(words: Iterable[str]) -> str:
    formatted: list[str] = []
    for index, word in enumerate(words):
        lower = word.lower()
        if index > 0 and lower in _SMALL_WORDS:
            formatted.append(lower)
        else:
            formatted.append(lower.capitalize())
    return " ".join(formatted)


def _normalize_segment(segment: str) -> str:
    candidate = _BULLET_PREFIX.sub("", segment).strip().strip(".:;,-")
    if not candidate:
        return ""

    for delimiter in (" because ", " so that ", " in order to ", " while ", " whereas "):
        lower = candidate.lower()
        if delimiter in lower:
            candidate = candidate[: lower.index(delimiter)].strip()
            break

    candidate = _SPACES.sub(" ", candidate)
    words = candidate.split(" ")
    while words and words[0].lower() in {"then", "next", "afterward", "finally", "and"}:
        words.pop(0)

    if not words:
        return ""

    if len(words) > 8:
        words = words[:8]

    return _title_case(words)


def extract_executive_steps(text: str, max_steps: int = 6) -> list[str]:
    if max_steps < 2:
        raise ValueError("max_steps must be at least 2")

    raw_segments = _SPLIT_PATTERN.split(text.strip())
    normalized = [_normalize_segment(segment) for segment in raw_segments]
    filtered = [segment for segment in normalized if segment]

    deduped: list[str] = []
    seen: set[str] = set()
    for segment in filtered:
        key = segment.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(segment)

    if not deduped:
        return ["Align on Objectives", "Map Key Process Stages", "Review and Approve Workflow"]

    if len(deduped) > max_steps:
        deduped = deduped[: max_steps - 1] + ["Finalize and Communicate Plan"]

    return deduped


def build_mermaid_flowchart(steps: list[str]) -> str:
    if not steps:
        raise ValueError("steps cannot be empty")

    lines = ["flowchart TD", '    N0(["Start"])']
    for index, step in enumerate(steps, start=1):
        safe_step = step.replace('"', "'")
        lines.append(f'    N{index}["{safe_step}"]')

    end_index = len(steps) + 1
    lines.append(f'    N{end_index}(["End"])')
    lines.append("    N0 --> N1")

    for index in range(1, len(steps)):
        lines.append(f"    N{index} --> N{index + 1}")

    lines.append(f"    N{len(steps)} --> N{end_index}")
    return "\n".join(lines)


def build_executive_workflow_diagram(text: str, max_steps: int = 6) -> str:
    steps = extract_executive_steps(text=text, max_steps=max_steps)
    return build_mermaid_flowchart(steps)
