from langsmith import get_current_run_tree, traceable
from langsmith.run_trees import RunTree

from app.agent import memory
from app.agent.guardrails import SAFE_FALLBACK_REPLY, screen_input, screen_output
from app.agent.intent_classifier import classify_intent
from app.agent.main_agent import run_main_agent
from app.agent.schemas import AgentRequest, AgentResult, ChatRequest, ChatResponse, IntentClassificationRequest
from app.config import settings


def _record_outcome(
    run: RunTree | None, *, blocked: bool, block_reason: str | None, retried_stricter: bool, needs_human: bool
) -> None:
    if not run:
        return
    run.metadata.update(
        app_version=settings.app_version,
        blocked=blocked,
        block_reason=block_reason,
        retried_stricter=retried_stricter,
        needs_human=needs_human,
    )
    run.tags.extend(tag for tag, on in (("blocked", blocked), ("needs_human", needs_human)) if on)


@traceable(name="handle_chat", run_type="chain")
def handle_chat(request: ChatRequest) -> ChatResponse:
    if run := get_current_run_tree():
        run.metadata["session_id"] = request.session_id
        if request.customer_id is not None:
            run.metadata["customer_id"] = request.customer_id
    screened = screen_input(request.message)
    if not screened.allowed:
        _record_outcome(run, blocked=True, block_reason=screened.reason, retried_stricter=False, needs_human=False)
        return ChatResponse(session_id=request.session_id, reply=screened.reply or "", intents=[], blocked=True)

    history = memory.get_history(request.session_id)
    if run:
        run.metadata["history_turns_sent"] = len(history)
    classification = classify_intent(IntentClassificationRequest(message=request.message, history=history))
    intents = [score.intent for score in classification.intents]
    if run:
        run.metadata["intents"] = [intent.value for intent in intents]

    agent_request = AgentRequest(
        message=request.message, history=history, intents=intents, customer_id=request.customer_id
    )

    def acceptable(result: AgentResult) -> bool:
        return screen_output(result.response.reply).allowed

    result = run_main_agent(agent_request)
    retried = not acceptable(result)
    if retried:
        result = run_main_agent(agent_request.model_copy(update={"stricter": True}))
    verdict = screen_output(result.response.reply)
    blocked = not verdict.allowed
    _record_outcome(
        run,
        blocked=blocked,
        block_reason=verdict.reason,
        retried_stricter=retried,
        needs_human=result.response.needs_human,
    )
    reply = SAFE_FALLBACK_REPLY if blocked else result.response.reply

    memory.append_exchange(request.session_id, request.message, reply)
    return ChatResponse(session_id=request.session_id, reply=reply, intents=intents, blocked=blocked)
