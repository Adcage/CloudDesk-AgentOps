INJECTION_PATTERNS: list[str] = [
    "ignore previous instructions",
    "disregard all above",
    "you are now",
    "system prompt:",
    "forget your instructions",
    "act as if",
    "pretend you are",
    "new instructions:",
]


def detect_injection(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in INJECTION_PATTERNS)