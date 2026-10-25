from app.agent.schemas import Intent, IntentClassification, IntentClassificationRequest, IntentScore
from app.clients.openai_client import get_openai
from app.config import settings
from app.prompts import render_prompt


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
    decision = get_openai().decisions.create(model=settings.intent_model, input=messages, questions=questions)

    scores = [
        IntentScore(intent=Intent(answer.name), probability=answer.probability)
        for answer in decision.answers
        if answer.type == "predicate" and answer.probability >= settings.intent_threshold
    ]
    if not scores:
        scores = [IntentScore(intent=Intent.OFF_TOPIC_ESCALATE, probability=1.0)]
    return IntentClassification(intents=sorted(scores, key=lambda s: s.probability, reverse=True))
