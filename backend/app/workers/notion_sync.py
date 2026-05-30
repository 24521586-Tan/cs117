"""Meeting analysis -> a Notion page (Summary + grouped To-do list).

Each task is a checkbox to_do with child blocks holding the deadline + source
slide and the verbatim quote. Requires a Notion database with columns:
Name (title), Date (date), Attendees (multi-select). See docs/notion-setup.md.
"""

from datetime import date

from notion_client import Client

from app.core.config import settings

_NOTION_APPEND_LIMIT = 100  # Notion caps children per append call


def _rich(text: str) -> list[dict]:
    # Notion rejects empty rich_text content; clamp length defensively.
    return [{"type": "text", "text": {"content": (text or "")[:2000]}}]


def _task_block(task: dict) -> dict:
    children = []

    meta_bits = []
    if task.get("deadline"):
        meta_bits.append(f"📅 {task['deadline']}")
    if task.get("slide") is not None:
        meta_bits.append(f"📑 Slide {task['slide']}")
    if meta_bits:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": _rich(" · ".join(meta_bits))},
        })

    if task.get("quote"):
        children.append({
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": _rich(task["quote"])},
        })

    block = {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": _rich(task.get("task", "")), "checked": False},
    }
    if children:
        block["to_do"]["children"] = children
    return block


def _build_children(analysis: dict) -> list[dict]:
    blocks: list[dict] = [
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": _rich("📌 Meeting Summary")}},
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": _rich(analysis.get("summary", ""))}},
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": _rich("✅ To-do List")}},
    ]

    for group in analysis.get("tasks_by_person", []):
        blocks.append({
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": _rich(f"👤 {group.get('person', 'Unassigned')}")},
        })
        for task in group.get("tasks", []):
            blocks.append(_task_block(task))

    return blocks


def create_meeting_page(analysis: dict) -> str:
    """Create the Notion page and return its URL."""
    if not settings.NOTION_TOKEN or not settings.NOTION_DATABASE_ID:
        raise RuntimeError("NOTION_TOKEN / NOTION_DATABASE_ID not set — cannot sync to Notion.")

    notion = Client(auth=settings.NOTION_TOKEN)
    attendees = analysis.get("attendees") or [g["person"] for g in analysis.get("tasks_by_person", [])]

    page = notion.pages.create(
        parent={"database_id": settings.NOTION_DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": analysis.get("title", "Meeting Notes")}}]},
            "Date": {"date": {"start": date.today().isoformat()}},
            "Attendees": {"multi_select": [{"name": a[:100]} for a in attendees]},
        },
    )
    page_id = page["id"]

    children = _build_children(analysis)
    for i in range(0, len(children), _NOTION_APPEND_LIMIT):
        notion.blocks.children.append(block_id=page_id, children=children[i:i + _NOTION_APPEND_LIMIT])

    return page.get("url", f"https://notion.so/{page_id.replace('-', '')}")
