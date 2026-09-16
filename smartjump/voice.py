"""Constrained voice-command interpretation for the Smart Jump prototype."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from smartjump.config import MAX_HEIGHT_IN, MIN_HEIGHT_IN


@dataclass(frozen=True)
class VoiceCommand:
    intent: str
    transcript: str
    height_in: Optional[int] = None


_ONES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

_TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
}


def _extract_height(text: str) -> Optional[int]:
    digit_match = re.search(r"\b(\d{1,3})\b", text)
    if digit_match:
        return int(digit_match.group(1))

    words = re.sub(r"[^a-z\s-]", " ", text).replace("-", " ").split()
    for index, word in enumerate(words):
        if word in _ONES:
            return _ONES[word]
        if word in _TENS:
            value = _TENS[word]
            if index + 1 < len(words) and words[index + 1] in _ONES:
                value += _ONES[words[index + 1]]
            return value
    return None


def interpret_voice_command(transcript: str) -> VoiceCommand:
    normalized = " ".join(transcript.lower().strip().split())
    if not normalized:
        raise ValueError("No voice command was detected.")

    if re.search(r"\b(stop|halt|emergency stop|cancel)\b", normalized):
        return VoiceCommand(intent="stop", transcript=transcript)

    if re.search(r"\b(status|current height|what height|system state)\b", normalized):
        return VoiceCommand(intent="status", transcript=transcript)

    if re.search(r"\b(set|raise|lower|move|height)\b", normalized):
        height = _extract_height(normalized)
        if height is None:
            raise ValueError("A height was not recognized.")
        if not MIN_HEIGHT_IN <= height <= MAX_HEIGHT_IN:
            raise ValueError(
                f"Height must be between {MIN_HEIGHT_IN} and {MAX_HEIGHT_IN} inches."
            )
        return VoiceCommand(intent="set_height", transcript=transcript, height_in=height)

    raise ValueError("Command not recognized. Try 'set 36 inches', 'status', or 'stop'.")

