FORBIDDEN_PATTERNS = [
    "ignore previous",
    "ignore all instructions",
    "system prompt",
    "reveal your instructions",
    "bypass",
    "disregard",
    "forget everything",
]


def check_injection(prompt: str) -> bool:
    """프롬프트에 금지어가 포함되어 있으면 True(위험)를 반환합니다."""
    prompt_lower = prompt.lower()
    return any(pattern in prompt_lower for pattern in FORBIDDEN_PATTERNS)
