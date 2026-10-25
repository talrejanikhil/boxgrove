import json

from app.agent.schemas import AgentRequest, AgentResponse, AgentResult, IntentOutcome, ToolCall
from app.clients.openai_client import get_openai
from app.config import settings
from app.prompts import render_prompt
from app.tools import TOOL_SPECS, TOOLS_BY_NAME


def run_tool(name: str, arguments: str) -> str:
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        return json.dumps({"error": f"Unknown tool {name}"})
    try:
        return json.dumps(tool.invoke(json.loads(arguments)), default=str)
    except Exception as e:  # tool boundary: report any failure to the model instead of crashing the turn
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


def run_main_agent(request: AgentRequest) -> AgentResult:
    client = get_openai()
    instructions = render_prompt("main_agent/system.md", customer_id=request.customer_id, stricter=request.stricter)
    conversation = [{"role": t.role, "content": t.content} for t in request.history]
    conversation.append({"role": "user", "content": request.message})

    outcomes: list[IntentOutcome] = []
    tool_calls: list[ToolCall] = []
    previous_id: str | None = None

    for position, intent in enumerate(request.intents, 1):
        directive = {
            "role": "developer",
            "content": render_prompt(
                "main_agent/handle_intent.md",
                intent=intent.value,
                position=position,
                total=len(request.intents),
                others=[i.value for i in request.intents if i != intent],
            ),
        }
        next_input = [*conversation, directive] if previous_id is None else [directive]
        outcome: IntentOutcome | None = None

        for _ in range(settings.max_tool_rounds + 1):
            response = client.responses.parse(
                model=settings.main_model,
                instructions=instructions,
                input=next_input,
                tools=TOOL_SPECS,
                text_format=IntentOutcome,
                previous_response_id=previous_id,
                reasoning={"effort": settings.main_reasoning_effort},
            )
            previous_id = response.id
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                outcome = response.output_parsed
                break
            next_input = []
            for call in calls:
                output = run_tool(call.name, call.arguments)
                tool_calls.append(ToolCall(name=call.name, arguments=call.arguments, output=output))
                next_input.append({"type": "function_call_output", "call_id": call.call_id, "output": output})

        if outcome is None:
            outcome = IntentOutcome(
                intent=intent,
                resolved=False,
                reply="I wasn't able to finish handling that request.",
                needs_human=True,
            )
        outcomes.append(outcome.model_copy(update={"intent": intent}))

    response = AgentResponse(
        reply="\n\n".join(o.reply for o in outcomes),
        outcomes=outcomes,
        needs_human=any(o.needs_human for o in outcomes),
    )
    return AgentResult(response=response, tool_calls=tool_calls)
