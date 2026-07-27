import pytest

from backend.ai import categorize, parse_task
from backend.ai.client import AIUnavailableError


class FakeToolUseBlock:
    def __init__(self, input_data):
        self.type = "tool_use"
        self.input = input_data


class FakeResponse:
    def __init__(self, input_data):
        self.content = [FakeToolUseBlock(input_data)]


class FakeClient:
    def __init__(self, response_input):
        self.response_input = response_input
        self.last_kwargs = None
        self.messages = self

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeResponse(self.response_input)


def test_parse_task_forces_tool_choice(monkeypatch):
    fake = FakeClient(
        {
            "title": "Call mom",
            "due_datetime": "2026-08-02T18:00:00",
            "priority": "medium",
            "tags": [],
            "category": None,
        }
    )
    monkeypatch.setattr(parse_task, "get_client", lambda: fake)

    result = parse_task.parse_task_text("remind me to call mom Sunday evening")

    assert result["title"] == "Call mom"
    assert fake.last_kwargs["tool_choice"] == {"type": "tool", "name": "record_task"}
    assert fake.last_kwargs["tools"][0]["name"] == "record_task"
    # forced tool_choice, not "auto" -- this is what guarantees no prose fallback path
    assert fake.last_kwargs["tool_choice"]["type"] == "tool"


def test_parse_task_raises_when_ai_unavailable(monkeypatch):
    monkeypatch.setattr(parse_task, "get_client", lambda: None)
    with pytest.raises(AIUnavailableError):
        parse_task.parse_task_text("anything")


def test_categorize_task_constrains_enum_to_real_categories(monkeypatch):
    fake = FakeClient({"category": "Work", "priority": "high", "reasoning": "has a deadline"})
    monkeypatch.setattr(categorize, "get_client", lambda: fake)

    result = categorize.categorize_task("Submit report", None, ["Work", "Home"])

    assert result["category"] == "Work"
    tool = fake.last_kwargs["tools"][0]
    assert tool["input_schema"]["properties"]["category"]["enum"] == ["Work", "Home", "Other"]
    assert fake.last_kwargs["tool_choice"] == {"type": "tool", "name": "assign_category"}


def test_categorize_task_raises_when_ai_unavailable(monkeypatch):
    monkeypatch.setattr(categorize, "get_client", lambda: None)
    with pytest.raises(AIUnavailableError):
        categorize.categorize_task("Anything", None, [])
