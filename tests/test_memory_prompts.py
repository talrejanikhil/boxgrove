import pytest
from jinja2 import UndefinedError

from app.agent import memory
from app.agent.schemas import Intent
from app.config import settings
from app.prompts import render_prompt


@pytest.fixture(autouse=True)
def clean_memory() -> None:
    memory.clear_all()


def test_memory_keeps_last_turns_per_session() -> None:
    for i in range(settings.history_turns + 3):
        memory.append_exchange("s1", f"q{i}", f"a{i}")
    history = memory.get_history("s1")
    assert len(history) == settings.history_turns * 2
    assert history[-1].content == f"a{settings.history_turns + 2}"
    assert memory.get_history("other") == []


def test_prompts_render_variables() -> None:
    assert "customer 7" in render_prompt("main_agent/system.md", customer_id=7, stricter=False)
    assert "Stricter mode" in render_prompt("main_agent/system.md", customer_id=None, stricter=True)
    assert "`policy_faq`" in render_prompt("intent_classifier/classify_intent.md", intent="policy_faq")


def test_prompt_missing_variable_fails() -> None:
    with pytest.raises(UndefinedError):
        render_prompt("main_agent/handle_intent.md", intent="policy_faq")


def test_taxonomy_in_prompt_matches_enum() -> None:
    text = render_prompt("intent_classifier/classify_intent.md", intent="x")
    assert all(f"- {i.value}:" in text for i in Intent)


def test_classifier_prompt_covers_conversation_recall() -> None:
    text = render_prompt("intent_classifier/classify_intent.md", intent="order_status")
    assert "recall or repeat something from earlier" in text


def test_intent_directive_names_other_intents() -> None:
    text = render_prompt("main_agent/handle_intent.md", intent="a", position=1, total=2, others=["policy_faq"])
    assert "policy_faq" in text
    solo = render_prompt("main_agent/handle_intent.md", intent="a", position=1, total=1, others=[])
    assert "separate steps" not in solo
