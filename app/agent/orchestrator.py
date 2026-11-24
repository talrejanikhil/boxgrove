from langsmith import get_current_run_tree, traceable

from app.agent import memory
from app.agent.guardrails import SAFE_FALLBACK_REPLY, screen_input, screen_output
from app.agent.intent_classifier import classify_intent
from app.agent.main_agent import run_main_agent
from app.agent.schemas import AgentRequest, AgentResult, ChatRequest, ChatResponse, IntentClassificationRequest


@traceable(name="handle_chat", run_type="chain")
def handle_chat(request: ChatRequest) -> ChatResponse:
    if run := get_current_run_tree():
        run.metadata["session_id"] = request.session_id
    screened = screen_input(request.message)
    if not screened.allowed:
        return ChatResponse(session_id=request.session_id, reply=screened.reply or "", intents=[], blocked=True)

    history = memory.get_history(request.session_id)
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
    if not acceptable(result):
        result = run_main_agent(agent_request.model_copy(update={"stricter": True}))
    blocked = not acceptable(result)
    reply = SAFE_FALLBACK_REPLY if blocked else result.response.reply

    memory.append_exchange(request.session_id, request.message, reply)
    return ChatResponse(session_id=request.session_id, reply=reply, intents=intents, blocked=blocked)
