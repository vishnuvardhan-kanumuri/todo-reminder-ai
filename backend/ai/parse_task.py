from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ai.client import AIUnavailableError, get_client
from backend.ai.tool_schemas import RECORD_TASK_TOOL
from backend.config import settings


def parse_task_text(text: str) -> dict:
    client = get_client()
    if client is None:
        raise AIUnavailableError("ANTHROPIC_API_KEY is not configured")

    now = datetime.now(ZoneInfo(settings.timezone))
    system = (
        f"The current date/time is {now.isoformat()} in timezone {settings.timezone}. "
        "Resolve any relative date or time reference in the user's text against this. "
        "Extract exactly one task using the record_task tool."
    )

    response = client.messages.create(
        model=settings.ai_model_parse,
        max_tokens=512,
        system=system,
        tools=[RECORD_TASK_TOOL],
        tool_choice={"type": "tool", "name": "record_task"},
        messages=[{"role": "user", "content": text}],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    return tool_use.input
