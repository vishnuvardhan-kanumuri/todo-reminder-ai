from backend.ai.client import AIUnavailableError, get_client
from backend.ai.tool_schemas import build_assign_category_tool
from backend.config import settings

FEW_SHOT_EXAMPLES = """Examples of how to judge priority (category naming follows the enum you're given, not these names):
- "Submit Q3 budget report to finance" -> priority: high (has an external deadline/dependency)
- "Pick up dry cleaning" -> priority: low (no deadline pressure)
- "Doctor appointment for annual checkup" -> priority: medium (scheduled, but not urgent)
- "Read chapter 4 of the SQL book" -> priority: low (self-paced)"""


def build_system_prompt(category_names: list[str]) -> str:
    categories_list = ", ".join(category_names) if category_names else "(none yet — use 'Other')"
    return (
        "You assign an existing category and a priority to a task. "
        f"The user's current categories are: {categories_list}. "
        "You must pick one of these exact names, or 'Other' if none fit — never invent a new name.\n\n"
        f"{FEW_SHOT_EXAMPLES}"
    )


def categorize_task(title: str, description: str | None, category_names: list[str]) -> dict:
    client = get_client()
    if client is None:
        raise AIUnavailableError("ANTHROPIC_API_KEY is not configured")

    tool = build_assign_category_tool(category_names)
    user_content = title if not description else f"{title}\n{description}"

    response = client.messages.create(
        model=settings.ai_model_categorize,
        max_tokens=256,
        system=build_system_prompt(category_names),
        tools=[tool],
        tool_choice={"type": "tool", "name": "assign_category"},
        messages=[{"role": "user", "content": user_content}],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    return tool_use.input
