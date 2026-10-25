import re
from dataclasses import dataclass

# Deterministic regex rules only, no LLM calls, so no added latency or cost.
# Production systems would layer LLM-based or dedicated guardrail tooling on top (see the production-readiness chapter).

BLOCKED_INPUT_REPLY = (
    "Sorry, I can't help with that request. I can help with Boxgrove products, orders, returns and store policies."
)
SAFE_FALLBACK_REPLY = (
    "I'm sorry, I can't give a reliable answer to that right now. "
    "Please contact Boxgrove support and they will be happy to help."
)


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str | None = None
    reply: str | None = None


INJECTION = re.compile(
    "|".join(
        [
            r"ignore\s+(?:(?:all|any|the|your)\s+){0,2}(?:previous|prior|above|earlier)\s+(?:instructions|prompts?|rules)",
            r"disregard\s+(?:(?:all|any|the|your)\s+){0,2}(?:(?:previous|prior|above)\s+)?(?:instructions|rules)",
            r"\byou\s+are\s+now\b",
            r"\bpretend\s+(?:to\s+be|you\s+are)\b",
            r"(?:reveal|show|print|repeat|leak|output)\s+(?:me\s+)?(?:(?:your|the)\s+)?(?:system|hidden|initial|original)\s+(?:prompt|instructions|message)",
            r"\bdeveloper\s+mode\b",
            r"\bjailbreak",
            r"</?\s*(?:system|assistant|developer)\s*>",
        ]
    ),
    re.IGNORECASE,
)
PII_SHAPES = re.compile(
    "|".join(
        [
            r"[\w.+-]{1,64}@[\w-]{1,63}(?:\.[\w-]{1,63}){1,4}",
            r"\b(?:\d[ -]?){13,16}\b",
            r"\b\d{3}-\d{2}-\d{4}\b",
            r"\b(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b",
        ]
    )
)


def screen_input(message: str) -> GuardrailResult:
    if INJECTION.search(message):
        return GuardrailResult(False, "prompt_injection", BLOCKED_INPUT_REPLY)
    return GuardrailResult(True)


def screen_output(text: str) -> GuardrailResult:
    if PII_SHAPES.search(text):
        return GuardrailResult(False, "pii_shape")
    return GuardrailResult(True)
