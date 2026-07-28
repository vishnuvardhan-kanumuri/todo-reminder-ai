from datetime import datetime
from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field
from sqlmodel import Session

from backend.db import engine
from backend.mcp_server import tools
from backend.models import TaskPriority, TaskStatus

mcp = MCPServer(
    "todo-reminder-ai",
    instructions=(
        "Tools for a personal todo/reminder app: task and category CRUD, plus two "
        "AI helpers (parse_task_text, categorize_task) that delegate to this app's "
        "own Claude-backed logic instead of you inferring structure yourself."
    ),
)


@mcp.tool()
def list_tasks(
    status: Annotated[TaskStatus | None, Field(description="Filter by status")] = None,
    category_id: Annotated[int | None, Field(description="Filter by category id")] = None,
    due_before: Annotated[
        datetime | None, Field(description="Only tasks due at/before this ISO 8601 datetime")
    ] = None,
    due_after: Annotated[
        datetime | None, Field(description="Only tasks due at/after this ISO 8601 datetime")
    ] = None,
    tag: Annotated[str | None, Field(description="Only tasks containing this tag")] = None,
) -> list[dict]:
    """List tasks, optionally filtered by status, category, due-date range, or tag."""
    with Session(engine) as session:
        return tools.list_tasks(
            session,
            status=status,
            category_id=category_id,
            due_before=due_before,
            due_after=due_after,
            tag=tag,
        )


@mcp.tool()
def get_task(task_id: Annotated[int, Field(description="Task id")]) -> dict:
    """Get a single task by id."""
    with Session(engine) as session:
        return tools.get_task(session, task_id)


@mcp.tool()
def create_task(
    title: Annotated[str, Field(description="Short, human-readable task title")],
    description: Annotated[str | None, Field(description="Longer free-text detail")] = None,
    due_datetime: Annotated[
        datetime | None, Field(description="ISO 8601 datetime this task is due")
    ] = None,
    priority: Annotated[TaskPriority, Field(description="Urgency")] = TaskPriority.medium,
    category_id: Annotated[int | None, Field(description="Existing category id")] = None,
    tags: Annotated[list[str] | None, Field(description="Freeform keyword tags")] = None,
    recurrence_rule: Annotated[
        str | None,
        Field(description="Recurrence grammar '<daily|weekly|monthly>[:<interval>]', e.g. 'weekly:2'"),
    ] = None,
) -> dict:
    """Create a new task."""
    with Session(engine) as session:
        return tools.create_task(
            session,
            title=title,
            description=description,
            due_datetime=due_datetime,
            priority=priority,
            category_id=category_id,
            tags=tags,
            recurrence_rule=recurrence_rule,
        )


@mcp.tool()
def update_task(
    task_id: Annotated[int, Field(description="Task id to update")],
    title: Annotated[str | None, Field(description="New title; omit to leave unchanged")] = None,
    description: Annotated[
        str | None, Field(description="New description; omit to leave unchanged")
    ] = None,
    clear_description: Annotated[
        bool, Field(description="Set true to clear description instead of setting it")
    ] = False,
    due_datetime: Annotated[
        datetime | None, Field(description="New due datetime; omit to leave unchanged")
    ] = None,
    clear_due_datetime: Annotated[
        bool, Field(description="Set true to clear due_datetime instead of setting it")
    ] = False,
    priority: Annotated[
        TaskPriority | None, Field(description="New priority; omit to leave unchanged")
    ] = None,
    status: Annotated[
        TaskStatus | None, Field(description="New status; omit to leave unchanged")
    ] = None,
    category_id: Annotated[
        int | None, Field(description="New category id; omit to leave unchanged")
    ] = None,
    clear_category: Annotated[
        bool, Field(description="Set true to clear category_id instead of setting it")
    ] = False,
    tags: Annotated[
        list[str] | None,
        Field(description="Replacement tag list; omit to leave unchanged, [] to clear"),
    ] = None,
    recurrence_rule: Annotated[
        str | None, Field(description="New recurrence rule; omit to leave unchanged")
    ] = None,
    clear_recurrence_rule: Annotated[
        bool, Field(description="Set true to clear recurrence_rule instead of setting it")
    ] = False,
) -> dict:
    """Partially update a task. Only the fields you pass are changed."""
    with Session(engine) as session:
        return tools.update_task(
            session,
            task_id,
            title=title,
            description=description,
            clear_description=clear_description,
            due_datetime=due_datetime,
            clear_due_datetime=clear_due_datetime,
            priority=priority,
            status=status,
            category_id=category_id,
            clear_category=clear_category,
            tags=tags,
            recurrence_rule=recurrence_rule,
            clear_recurrence_rule=clear_recurrence_rule,
        )


@mcp.tool()
def delete_task(task_id: Annotated[int, Field(description="Task id to delete")]) -> dict:
    """Permanently delete a task."""
    with Session(engine) as session:
        return tools.delete_task(session, task_id)


@mcp.tool()
def complete_task(task_id: Annotated[int, Field(description="Task id to mark complete")]) -> dict:
    """Mark a task completed. If it has a recurrence_rule, spawns the next occurrence."""
    with Session(engine) as session:
        return tools.complete_task(session, task_id)


@mcp.tool()
def snooze_task(
    task_id: Annotated[int, Field(description="Task id to snooze")],
    until: Annotated[datetime, Field(description="ISO 8601 datetime to snooze until")],
) -> dict:
    """Snooze a task until a later datetime."""
    with Session(engine) as session:
        return tools.snooze_task(session, task_id, until)


@mcp.tool()
def list_categories() -> list[dict]:
    """List all categories."""
    with Session(engine) as session:
        return tools.list_categories(session)


@mcp.tool()
def create_category(
    name: Annotated[str, Field(description="Category name")],
    color: Annotated[str | None, Field(description="Display color, e.g. a hex code")] = None,
) -> dict:
    """Create a new category."""
    with Session(engine) as session:
        return tools.create_category(session, name, color)


@mcp.tool()
def delete_category(category_id: Annotated[int, Field(description="Category id to delete")]) -> dict:
    """Permanently delete a category."""
    with Session(engine) as session:
        return tools.delete_category(session, category_id)


@mcp.tool()
def parse_task_text(
    text: Annotated[str, Field(description="Free-text task request, e.g. 'remind me to call mom Sunday evening'")],
) -> dict:
    """Extract a structured task proposal from free text using this app's own
    Claude-backed parser (forced tool_choice, never prose). Raises if no
    ANTHROPIC_API_KEY is configured on this app."""
    return tools.parse_task_text(text)


@mcp.tool()
def categorize_task(
    task_id: Annotated[int, Field(description="Existing task id to categorize")],
    apply: Annotated[
        bool, Field(description="If true, apply the suggested category/priority to the task")
    ] = False,
) -> dict:
    """Suggest a category and priority for an existing task from the user's real
    categories, using this app's own Claude-backed logic. Raises if no
    ANTHROPIC_API_KEY is configured on this app."""
    with Session(engine) as session:
        return tools.categorize_task(session, task_id, apply=apply)
