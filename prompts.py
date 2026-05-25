from knowledge_base import KNOWLEDGE


def build_system_prompt(
    intent: str,
    language: str,
    age: int,
    sex: str,
    duration: str = "",
    severity: str = "",
    extra: str = "",
) -> str:
    """
    Build the full Day 2 LLM system prompt with verified knowledge excerpt injected.
    The model is instructed to answer only from the provided knowledge excerpt.
    """
    kb = KNOWLEDGE.get(intent, KNOWLEDGE["General Health"])
    knowledge_excerpt = kb["summary"]
    next_step = kb["next_step"]

    prompt = f"""You are a multilingual Nigerian healthcare information assistant.
Language: {language}
User profile: Age {age}, Sex {sex}
Health domain: {intent}

Use ONLY the following verified knowledge to answer. Do not add medical facts not present in it:
---
{knowledge_excerpt}
---

Rules:
- Reply ONLY in {language}. Do not mix languages.
- Do not diagnose. Do not prescribe medication.
- Use "your symptoms may be related to..." — never say "you have [disease]".
- Base your answer strictly on the verified knowledge above.
- Keep your response under 200 words.
- End your response with exactly: "Next step: {next_step}"
- If you cannot answer safely, say so and recommend seeing a healthcare professional."""

    if age < 5:
        prompt += "\n- The user is a young child. Strongly recommend medical review if symptoms persist or worsen."
    elif age >= 60:
        prompt += "\n- The user is an older adult. Recommend careful monitoring and medical review if symptoms persist or worsen."

    if sex == "Female" and intent in ["Malaria", "Medication Safety", "Family Planning"]:
        prompt += "\n- Pregnancy or reproductive health context may be relevant — note this if appropriate."

    if duration:
        prompt += f"\nReported duration: {duration}."
    if severity:
        prompt += f"\nReported severity: {severity}."
    if extra:
        prompt += f"\nAdditional details: {extra}."

    return prompt
