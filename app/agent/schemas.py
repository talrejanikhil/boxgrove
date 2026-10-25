from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Intent(StrEnum):
    PRODUCT_QUESTION = "product_question"
    ORDER_STATUS = "order_status"
    RETURN_REQUEST = "return_request"
    POLICY_FAQ = "policy_faq"
    RECOMMENDATION = "recommendation"
    SMALL_TALK = "small_talk"
    OFF_TOPIC_ESCALATE = "off_topic_escalate"


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class IntentClassificationRequest(BaseModel):
    message: str
    history: list[Turn]


class IntentScore(BaseModel):
    intent: Intent
    probability: float


class IntentClassification(BaseModel):
    intents: list[IntentScore]


class AgentRequest(BaseModel):
    message: str
    history: list[Turn]
    intents: list[Intent]
    customer_id: int | None = None
    stricter: bool = False


class IntentOutcome(BaseModel):
    intent: Intent
    resolved: bool
    reply: str
    needs_human: bool


class AgentResponse(BaseModel):
    reply: str
    outcomes: list[IntentOutcome]
    needs_human: bool


class ToolCall(BaseModel):
    name: str
    arguments: str
    output: str


class AgentResult(BaseModel):
    response: AgentResponse
    tool_calls: list[ToolCall]


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2000)
    customer_id: int | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intents: list[Intent]
    blocked: bool = False
