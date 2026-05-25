import os
import re
from groq import Groq
from prompts import build_system_prompt


# ---------------------------------------------------------------------------
# Safety guardrail
# ---------------------------------------------------------------------------

_UNSAFE_PATTERNS = [
    re.compile(r"\byou have\b", re.IGNORECASE),
    re.compile(r"\byou are diagnosed\b", re.IGNORECASE),
    re.compile(r"\bprescription\b", re.IGNORECASE),
    # "take [Drug]" — "take" followed by a capitalized word (likely a drug name)
    re.compile(r"\btake\s+[A-Z][a-z]{2,}\b"),
]

_SAFE_FALLBACK = (
    "I'm not able to confirm a diagnosis. Please consult a healthcare professional."
)


def safety_check(response_text: str) -> str:
    """
    Post-process LLM output to catch unsafe diagnostic or prescriptive language.
    If any unsafe pattern is detected the entire response is replaced with a
    safe fallback message.
    """
    for pattern in _UNSAFE_PATTERNS:
        if pattern.search(response_text):
            return _SAFE_FALLBACK
    return response_text


def ask_llm(
    intent: str,
    language: str,
    age: int,
    sex: str,
    user_message: str,
    duration: str = "",
    severity: str = "",
    extra: str = "",
) -> str | None:
    """
    Call Groq API and return the response text.
    Returns None on any error or if GROQ_API_KEY is not set,
    signalling the caller to use the hardcoded fallback.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        client = Groq(api_key=api_key)
        system_prompt = build_system_prompt(
            intent=intent,
            language=language,
            age=age,
            sex=sex,
            duration=duration,
            severity=severity,
            extra=extra,
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        return safety_check(completion.choices[0].message.content)
    except Exception:
        return None
