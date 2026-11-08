
from types import SimpleNamespace

from personaforge.orchestrator import Orchestrator


class FakeClaude:
    """Simulate Claude tool calling without an API key."""

    def __init__(self):
        self.calls = 0

    def create_message(self, system, messages, tools, max_tokens=2048):
        self.calls += 1

        if self.calls == 1:
            return SimpleNamespace(
                stop_reason="tool_use",
                content=[
                    SimpleNamespace(
                        type="tool_use",
                        id="tool_123",
                        name="list_personas",
                        input={},
                    )
                ],
            )

        assert messages[-1]["content"][0]["type"] == "tool_result"
        assert messages[-1]["content"][0]["tool_use_id"] == "tool_123"

        return SimpleNamespace(
            stop_reason="end_turn",
            content=[
                SimpleNamespace(
                    type="text",
                    text="Here are your personas.",
                )
            ],
        )


def test_claude_can_call_list_personas(tmp_path):
    llm = FakeClaude()
    orchestrator = Orchestrator(llm, persona_dir=tmp_path)

    result = orchestrator.handle("Show me my personas")

    assert llm.calls == 2
    assert result.reply == "Here are your personas."


def test_claude_can_call_multiple_tools(tmp_path):
    class MultiToolClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, system, messages, tools, max_tokens=2048):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="tool_1",
                            name="list_personas",
                            input={},
                        ),
                        SimpleNamespace(
                            type="tool_use",
                            id="tool_2",
                            name="list_personas",
                            input={},
                        ),
                    ],
                )

            results = messages[-1]["content"]
            assert len(results) == 2
            assert {r["tool_use_id"] for r in results} == {
                "tool_1", "tool_2"
            }

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="Both actions completed.",
                    )
                ],
            )

    llm = MultiToolClaude()
    orchestrator = Orchestrator(llm, persona_dir=tmp_path)

    result = orchestrator.handle("List my personas twice")

    assert llm.calls == 2
    assert result.reply == "Both actions completed."


def test_claude_can_ask_for_clarification(tmp_path):
    class ClarifyingClaude:
        def create_message(self, system, messages, tools, max_tokens=2048):
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="What kind of persona would you like to create?",
                    )
                ],
            )

    orchestrator = Orchestrator(
        ClarifyingClaude(),
        persona_dir=tmp_path,
    )

    result = orchestrator.handle("Create a persona")

    assert result.reply == (
        "What kind of persona would you like to create?"
    )

def test_claude_remembers_previous_messages(tmp_path):
    class MemoryClaude:
        def __init__(self):
            self.calls = []

        def create_message(self, system, messages, tools, max_tokens=2048):
            self.calls.append(list(messages))

            if len(self.calls) == 1:
                reply = "What kind of persona would you like to create?"
            else:
                assert messages[0] == {
                    "role": "user",
                    "content": "Create a persona",
                }
                assert messages[1] == {
                    "role": "assistant",
                    "content": "What kind of persona would you like to create?",
                }
                assert messages[2] == {
                    "role": "user",
                    "content": "A pediatric nurse",
                }
                reply = "I'll create a pediatric nurse persona."

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(type="text", text=reply)
                ],
            )

    llm = MemoryClaude()
    orchestrator = Orchestrator(llm, persona_dir=tmp_path)

    orchestrator.handle("Create a persona")
    result = orchestrator.handle("A pediatric nurse")

    assert len(llm.calls) == 2
    assert result.reply == "I'll create a pediatric nurse persona."


def test_create_persona_tool_executes(tmp_path, monkeypatch):
    from personaforge import orchestrator as module

    class FakeCreator:
        def __init__(self):
            self.calls = 0

        def create_message(self, system, messages, tools, max_tokens=2048):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="create_1",
                            name="create_persona",
                            input={"description": "a pediatric nurse"},
                        )
                    ],
                )

            assert "Created" in messages[-1]["content"][0]["content"]

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="Your nurse persona is ready.",
                    )
                ],
            )

    descriptions = []

    def fake_generate(description, llm):
        descriptions.append(description)
        return SimpleNamespace(
            name="Alex",
            role="Nurse",
            summary="A pediatric nurse.",
        )

    monkeypatch.setattr(module, "generate_persona", fake_generate)
    monkeypatch.setattr(
        module,
        "save_persona",
        lambda spec, directory: directory / "alex.json",
    )

    orchestrator = Orchestrator(FakeCreator(), persona_dir=tmp_path)
    result = orchestrator.handle("Create a pediatric nurse")

    assert descriptions == ["a pediatric nurse"]
    assert result.reply == "Your nurse persona is ready."


def test_conversation_tool_uses_requested_settings(tmp_path, monkeypatch):
    from personaforge import orchestrator as module

    class FakeConversationClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, system, messages, tools, max_tokens=2048):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="conversation_1",
                            name="start_conversation",
                            input={
                                "participants": ["Alex", "Jordan"],
                                "topic": "patient communication",
                                "turns": 10,
                            },
                        )
                    ],
                )

            assert messages[-1]["content"][0]["type"] == "tool_result"

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="Conversation completed.",
                    )
                ],
            )

    captured = {}

    def fake_converse(self, topic, who=None, turns=6, on_turn=None, on_start=None):
        captured.update(topic=topic, who=who, turns=turns)
        return module.Result(reply="Conversation ran.")

    monkeypatch.setattr(module.Orchestrator, "_converse", fake_converse)

    orchestrator = Orchestrator(FakeConversationClaude(), persona_dir=tmp_path)
    result = orchestrator.handle("Have Alex and Jordan discuss patient communication for 10 turns")

    assert captured == {
        "topic": "patient communication",
        "who": ["Alex", "Jordan"],
        "turns": 10,
    }
    assert result.reply == "Conversation completed."



def test_asks_to_choose_when_more_than_two_personas(tmp_path):
    from personaforge import PersonaSpec, save_persona
    from personaforge.llm import ScriptedLLM

    for name in ["Alice", "Bob", "Charlie"]:
        save_persona(
            PersonaSpec(
                name=name,
                role="doctor",
                summary="",
                body="Test persona",
            ),
            tmp_path,
        )

    orchestrator = Orchestrator(
        llm=ScriptedLLM(replies=[]),
        persona_dir=tmp_path,
    )

    result = orchestrator._converse(topic="patient care")

    assert result.conversation is None
    assert "Which personas should participate?" in result.reply
    assert "Alice" in result.reply
    assert "Bob" in result.reply
    assert "Charlie" in result.reply



def test_tool_result_is_remembered_across_messages(tmp_path):
    class MemoryToolClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, system, messages, tools, max_tokens=2048):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="list_1",
                            name="list_personas",
                            input={},
                        )
                    ],
                )

            if self.calls == 2:
                return SimpleNamespace(
                    stop_reason="end_turn",
                    content=[
                        SimpleNamespace(
                            type="text",
                            text="I've checked your personas.",
                        )
                    ],
                )

            assert messages[1]["role"] == "assistant"
            assert messages[1]["content"][0].id == "list_1"
            assert messages[2]["role"] == "user"
            assert messages[2]["content"][0]["tool_use_id"] == "list_1"
            assert messages[-1]["content"] == "What did you find?"

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="I remember checking your personas.",
                    )
                ],
            )

    llm = MemoryToolClaude()
    orchestrator = Orchestrator(llm, persona_dir=tmp_path)

    orchestrator.handle("List my personas")
    result = orchestrator.handle("What did you find?")

    assert llm.calls == 3
    assert result.reply == "I remember checking your personas."


def test_claude_preserves_conversation_result(monkeypatch):
    from types import SimpleNamespace
    from personaforge.orchestrator import Orchestrator, Result

    class FakeClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="tool_1",
                            name="start_conversation",
                            input={
                                "participants": ["Alice", "Bob"],
                                "topic": "AI in healthcare",
                                "turns": 4,
                            },
                        )
                    ],
                )
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[SimpleNamespace(type="text", text="Conversation complete.")],
            )

    conversation = object()

    def fake_execute(self, name, arguments, on_turn=None, on_start=None):
        return Result(
            reply="Conversation saved.",
            events=["conversation saved"],
            conversation=conversation,
        )

    monkeypatch.setattr(Orchestrator, "_execute_tool", fake_execute)

    orchestrator = Orchestrator(FakeClaude())
    result = orchestrator.handle("Have Alice and Bob discuss AI in healthcare.")

    assert result.conversation is conversation
    assert result.events == ["conversation saved"]
    assert result.reply == "Conversation complete."

def test_claude_api_failure_returns_helpful_message():
    from personaforge.orchestrator import Orchestrator

    class FailingClaude:
        def create_message(self, **kwargs):
            raise ConnectionError("Simulated API outage")

    orchestrator = Orchestrator(FailingClaude())
    result = orchestrator.handle("Create a doctor persona")

    assert "Unable to contact Claude" in result.reply
    assert "ConnectionError" in result.reply
    assert result.conversation is None

def test_claude_api_failure_after_tool_preserves_results(monkeypatch):
    from types import SimpleNamespace
    from personaforge.orchestrator import Orchestrator, Result

    class FailingAfterToolClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, **kwargs):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="tool_1",
                            name="start_conversation",
                            input={
                                "participants": ["Alice", "Bob"],
                                "topic": "AI in healthcare",
                                "turns": 4,
                            },
                        )
                    ],
                )

            raise ConnectionError("Simulated API outage")

    conversation = object()

    def fake_execute(self, name, arguments, on_turn=None, on_start=None):
        return Result(
            reply="Conversation saved.",
            events=["conversation saved"],
            conversation=conversation,
        )

    monkeypatch.setattr(Orchestrator, "_execute_tool", fake_execute)

    orchestrator = Orchestrator(FailingAfterToolClaude())
    result = orchestrator.handle("Have Alice and Bob discuss AI in healthcare.")

    assert "Unable to contact Claude" in result.reply
    assert result.conversation is conversation
    assert result.events == ["conversation saved"]

def test_claude_tool_execution_failure_is_handled(tmp_path, monkeypatch):
    class ToolCallingClaude:
        def __init__(self):
            self.calls = 0

        def create_message(self, **kwargs):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id="tool_failure_1",
                            name="list_personas",
                            input={},
                        )
                    ],
                )

            tool_result = kwargs["messages"][-1]["content"][0]
            assert tool_result["tool_use_id"] == "tool_failure_1"
            assert "Tool execution failed: RuntimeError" in tool_result["content"]

            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="Sorry, I couldn't complete that action.",
                    )
                ],
            )

    def failing_tool(self, name, arguments, on_turn=None, on_start=None):
        raise RuntimeError("Simulated tool failure")

    monkeypatch.setattr(Orchestrator, "_execute_tool", failing_tool)

    orchestrator = Orchestrator(ToolCallingClaude(), persona_dir=tmp_path)
    result = orchestrator.handle("List my personas")

    assert result.reply == "Sorry, I couldn't complete that action."