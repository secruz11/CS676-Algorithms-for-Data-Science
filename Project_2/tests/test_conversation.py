"""
Tests for the conversation loop and the orchestrator's intent routing.

Everything runs against ScriptedLLM, so the whole suite is offline and free.
"""

import pytest

from personaforge import (
    Orchestrator,
    PersonaSpec,
    agent_from_spec,
    run_conversation,
    save_persona,
    save_transcript,
)
from personaforge.llm import ScriptedLLM

PERSONA_MD = """---
name: {name}
role: {role}
summary: a summary
---

# {name}
Body text.
"""


def two_agents(replies=None):
    llm = ScriptedLLM(replies=replies or ["line A", "line B"])
    a = agent_from_spec(PersonaSpec(name="Alice", role="doctor", summary="", body="A"), llm)
    b = agent_from_spec(PersonaSpec(name="Bob", role="patient", summary="", body="B"), llm)
    return a, b, llm


def test_conversation_alternates_speakers():
    a, b, _ = two_agents()
    convo = run_conversation([a, b], topic="the results", turns=4)

    assert [t.speaker for t in convo.turns] == ["Alice", "Bob", "Alice", "Bob"]


def test_conversation_respects_turn_count():
    a, b, _ = two_agents()
    assert len(run_conversation([a, b], topic="x", turns=5).turns) == 5


def test_conversation_needs_two_agents():
    a, _, _ = two_agents()
    with pytest.raises(ValueError):
        run_conversation([a], topic="x", turns=2)


def test_on_turn_fires_per_turn():
    a, b, _ = two_agents()
    seen = []
    run_conversation([a, b], topic="x", turns=3, on_turn=seen.append)

    assert len(seen) == 3
    assert seen[0].speaker == "Alice"


def test_topic_reaches_the_agents():
    """The scene turn must be visible to the first speaker."""
    a, b, llm = two_agents()
    run_conversation([a, b], topic="UNIQUE_TOPIC_MARKER", turns=1)

    first_call = llm.calls[0]["messages"]
    assert any("UNIQUE_TOPIC_MARKER" in m["content"] for m in first_call)


def test_transcript_contains_every_line():
    a, b, _ = two_agents(replies=["hello", "hi there"])
    convo = run_conversation([a, b], topic="greetings", turns=2)
    text = convo.transcript()

    assert "Alice" in text and "Bob" in text
    assert "hello" in text and "hi there" in text


def test_save_transcript_writes_a_file(tmp_path):
    a, b, _ = two_agents()
    convo = run_conversation([a, b], topic="x", turns=2)
    path = save_transcript(convo, tmp_path)

    assert path.exists()
    assert "Alice" in path.read_text(encoding="utf-8")


# -- orchestrator routing -----------------------------------------------------


def test_create_persona_writes_a_file(tmp_path):
    llm = ScriptedLLM(replies=[PERSONA_MD.format(name="Maria Delgado", role="patient")])
    orch = Orchestrator(llm=llm, persona_dir=tmp_path)

    result = orch.handle("create a persona patient with back pain")

    assert "Maria Delgado" in result.reply
    assert (tmp_path / "maria-delgado.md").exists()


def test_list_personas_reports_what_exists(tmp_path):
    save_persona(PersonaSpec(name="Maria Delgado", role="patient", summary="s", body="b"), tmp_path)
    orch = Orchestrator(llm=ScriptedLLM(), persona_dir=tmp_path)

    assert "Maria Delgado" in orch.handle("list personas").reply


def test_list_personas_when_empty(tmp_path):
    orch = Orchestrator(llm=ScriptedLLM(), persona_dir=tmp_path)
    assert "No personas yet" in orch.handle("list personas").reply


def test_conversation_requires_two_personas(tmp_path):
    save_persona(PersonaSpec(name="Solo", role="patient", summary="", body="b"), tmp_path)
    orch = Orchestrator(llm=ScriptedLLM(), persona_dir=tmp_path)

    assert "at least two" in orch.handle("have them talk about the weather").reply


def test_conversation_runs_with_two_personas(tmp_path):
    for name, role in [("Alice Adams", "doctor"), ("Bob Brown", "patient")]:
        save_persona(PersonaSpec(name=name, role=role, summary="", body="b"), tmp_path)

    orch = Orchestrator(llm=ScriptedLLM(replies=["a line"]), persona_dir=tmp_path)
    result = orch.handle("have them talk about the test results")

    assert result.conversation is not None
    assert len(result.conversation.turns) == 6
    assert (tmp_path / "conversation.md").exists()


def test_named_participants_are_resolved(tmp_path):
    for name, role in [("Alice Adams", "doctor"), ("Bob Brown", "patient"), ("Carol Chen", "nurse")]:
        save_persona(PersonaSpec(name=name, role=role, summary="", body="b"), tmp_path)

    orch = Orchestrator(llm=ScriptedLLM(replies=["x"]), persona_dir=tmp_path)
    result = orch.handle("start a conversation between Carol and Bob about the chart")

    assert result.conversation is not None
    assert set(result.conversation.participants) == {"Carol Chen", "Bob Brown"}


def test_unknown_participant_is_reported(tmp_path):
    for name in ["Alice Adams", "Bob Brown"]:
        save_persona(PersonaSpec(name=name, role="x", summary="", body="b"), tmp_path)

    orch = Orchestrator(llm=ScriptedLLM(), persona_dir=tmp_path)
    result = orch.handle("start a conversation between Zaphod and Bob about lunch")

    assert "couldn't find" in result.reply


def test_unmatched_input_falls_through_to_chat(tmp_path):
    llm = ScriptedLLM(replies=["Tell me who you want to build."])
    orch = Orchestrator(llm=llm, persona_dir=tmp_path)

    result = orch.handle("hello, what is this thing?")

    assert result.reply == "Tell me who you want to build."
    assert result.conversation is None

def test_final_turn_receives_closing_instruction():
    a, b, llm = two_agents(replies=["First response", "Final response"])

    convo = run_conversation([a, b], topic="caregiver burnout", turns=2)

    assert len(convo.turns) == 2

    first_messages = llm.calls[0]["messages"]
    final_messages = llm.calls[1]["messages"]

    assert not any(
        "This is the final turn" in m["content"]
        for m in first_messages
    )

    assert any(
        "This is the final turn" in m["content"]
        for m in final_messages
    )

    assert convo.turns[-1].text == "Final response"

def test_conversation_includes_topic_coverage_guidance():
    a, b, llm = two_agents()

    run_conversation(
        [a, b],
        topic="caregiver burnout, nighttime confusion, and outside help",
        turns=2,
    )

    for call in llm.calls:
        messages = call["messages"]
        content = " ".join(m["content"] for m in messages)

        assert "caregiver burnout" in content
        assert "nighttime confusion" in content
        assert "outside help" in content
        assert "meaningfully addresses all the themes" in content

def test_conversation_guidance_changes_with_progress():
    a, b, llm = two_agents()

    run_conversation([a, b], topic="three important themes", turns=6)

    messages = [
        " ".join(m["content"] for m in call["messages"])
        for call in llm.calls
    ]

    assert "Begin naturally" in messages[0]
    assert "Do not leave important" in messages[1]
    assert "Address unresolved themes now" in messages[3]
    assert "This is the final turn" in messages[5]

    assert "This is the final turn" not in messages[0]
    assert "This is the final turn" not in messages[4]

def test_transcript_includes_simulation_disclaimer():
    a, b, _ = two_agents(replies=["Hello", "Hi"])

    convo = run_conversation([a, b], topic="healthcare", turns=2)
    transcript = convo.transcript()

    assert "Simulation notice" in transcript
    assert "AI-generated fiction" in transcript
    assert "medical, legal, or safety advice" in transcript
    assert "Alice" in transcript
    assert "Bob" in transcript


def test_shared_context_reaches_all_agents():
    a, b, llm = two_agents()

    run_conversation(
        [a, b],
        topic="caregiver burnout",
        turns=2,
        shared_context="The patient's name is Delphine.",
    )

    assert len(llm.calls) == 2

    for call in llm.calls:
        content = " ".join(
            message["content"] for message in call["messages"]
        )
        assert "The patient's name is Delphine." in content
        assert "Shared background known to all participants" in content

