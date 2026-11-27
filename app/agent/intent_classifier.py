from langsmith import traceable
from openai.types import Decision

from app.agent.schemas import Intent, IntentClassification, IntentClassificationRequest, IntentScore
from app.clients.openai_client import get_openai
from app.config import settings
from app.prompts import render_prompt


def _llm_inputs(inputs: dict) -> dict:
    return {"messages": inputs["messages"][-1:]}


def _llm_outputs(decision: Decision) -> dict:
    usage = decision.usage
    return {
        "answers": [a.model_dump() for a in decision.answers],
        "model": decision.model,
        "usage_metadata": {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "input_token_details": {"cache_read": usage.input_tokens_details.cached_tokens},
            "output_token_details": {"reasoning": usage.output_tokens_details.reasoning_tokens},
        },
    }


@traceable(
    name="decisions_create",
    run_type="llm",
    metadata={"ls_provider": "openai", "ls_model_name": settings.intent_model},
    process_inputs=_llm_inputs,
    process_outputs=_llm_outputs,
)
def _decide(messages: list[dict], questions: list[dict]) -> Decision:
    return get_openai().decisions.create(model=settings.intent_model, input=messages, questions=questions)


@traceable(
    name="classify_intent",
    run_type="chain",
    process_inputs=lambda inputs: inputs["request"].model_dump(exclude={"history"}),
)
def classify_intent(request: IntentClassificationRequest) -> IntentClassification:
    messages = [{"role": t.role, "content": t.content} for t in request.history]
    messages.append({"role": "user", "content": request.message})
    questions = [
        {
            "type": "predicate",
            "name": intent.value,
            "instructions": render_prompt("intent_classifier/classify_intent.md", intent=intent.value),
        }
        for intent in Intent
    ]
    decision = _decide(messages, questions)

    scores = [
        IntentScore(intent=Intent(answer.name), probability=answer.probability)
        for answer in decision.answers
        if answer.type == "predicate" and answer.probability >= settings.intent_threshold
    ]
    if not scores:
        scores = [IntentScore(intent=Intent.OFF_TOPIC_ESCALATE, probability=1.0)]
    return IntentClassification(intents=sorted(scores, key=lambda s: s.probability, reverse=True))
