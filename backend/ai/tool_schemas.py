RECORD_TASK_TOOL = {
    "name": "record_task",
    "description": "Extract exactly one structured task from a user's free-text request.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short, human-readable task title.",
            },
            "due_datetime": {
                "type": ["string", "null"],
                "description": (
                    "ISO 8601 datetime (no timezone offset), resolved from any relative "
                    "reference ('Sunday evening', 'tomorrow') against the current date/time "
                    "given in the system prompt. Null if no due date/time was mentioned."
                ),
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Inferred urgency. Default to 'medium' if unclear.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Short freeform keywords. Empty array if none are obvious.",
            },
            "category": {
                "type": ["string", "null"],
                "description": "Best-guess category name, or null if unclear.",
            },
        },
        "required": ["title", "priority", "tags"],
    },
}


def build_assign_category_tool(category_names: list[str]) -> dict:
    return {
        "name": "assign_category",
        "description": "Assign the best-fit category and priority for a task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [*category_names, "Other"],
                    "description": "Must be one of the user's existing categories, or 'Other'.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
                "reasoning": {
                    "type": "string",
                    "description": "One sentence explaining the choice.",
                },
            },
            "required": ["category", "priority"],
        },
    }
