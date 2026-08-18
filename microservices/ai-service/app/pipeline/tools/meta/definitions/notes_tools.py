import uuid
from typing import Dict, Any, List, Optional

_NOTES_STORE: Dict[str, Dict[str, Any]] = {}


def notes_create(
    title: str,
    content: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create a new note item.
    
    Args:
        title: Note title.
        content: Text content of note.
        tags: Optional list of tag keywords.
    """
    if not title or not title.strip():
        return {"error": "Note title is required."}

    note_id = f"note_{uuid.uuid4().hex[:8]}"
    note = {
        "note_id": note_id,
        "title": title.strip(),
        "content": content.strip() if content else "",
        "tags": tags or []
    }
    _NOTES_STORE[note_id] = note

    return {"success": True, "note": note}


def notes_search(query: str) -> List[Dict[str, Any]]:
    """Search notes by title, content, or tag keyword.
    
    Args:
        query: Search string.
    """
    if not query or not query.strip():
        return list(_NOTES_STORE.values())

    q = query.lower().strip()
    results = []
    for note in _NOTES_STORE.values():
        title_match = q in note["title"].lower()
        content_match = q in note["content"].lower()
        tag_match = any(q in tag.lower() for tag in note.get("tags", []))
        if title_match or content_match or tag_match:
            results.append(note)

    return results


def notes_update(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Update an existing note item.
    
    Args:
        note_id: Note ID to modify.
        title: Optional new title.
        content: Optional new content.
        tags: Optional new tags list.
    """
    if note_id not in _NOTES_STORE:
        return {"error": f"Note ID '{note_id}' not found."}

    note = _NOTES_STORE[note_id]
    if title:
        note["title"] = title.strip()
    if content is not None:
        note["content"] = content.strip()
    if tags is not None:
        note["tags"] = tags

    return {"success": True, "note": note}
