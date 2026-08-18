import uuid
from typing import Dict, Any, List, Optional

_CALENDAR_STORE: Dict[str, Dict[str, Any]] = {}


def calendar_create(
    title: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new calendar event.
    
    Args:
        title: Event title.
        start_time: Start time string (ISO 8601 or YYYY-MM-DD HH:MM).
        end_time: End time string.
        description: Optional event description.
        location: Optional location string.
    """
    if not title or not title.strip():
        return {"error": "Title is required."}

    event_id = f"evt_{uuid.uuid4().hex[:8]}"
    event = {
        "event_id": event_id,
        "title": title.strip(),
        "start_time": start_time.strip(),
        "end_time": end_time.strip(),
        "description": description or "",
        "location": location or ""
    }
    _CALENDAR_STORE[event_id] = event

    return {"success": True, "event": event}


def calendar_search(query: str) -> List[Dict[str, Any]]:
    """Search calendar events by title or keyword.
    
    Args:
        query: Search string.
    """
    if not query or not query.strip():
        return list(_CALENDAR_STORE.values())

    q = query.lower().strip()
    return [
        evt for evt in _CALENDAR_STORE.values()
        if q in evt["title"].lower() or q in evt.get("description", "").lower()
    ]


def calendar_update(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Update details of an existing calendar event.
    
    Args:
        event_id: Unique event ID.
        title: Optional new title.
        start_time: Optional new start time.
        end_time: Optional new end time.
        description: Optional new description.
        location: Optional new location.
    """
    if event_id not in _CALENDAR_STORE:
        return {"error": f"Event ID '{event_id}' not found."}

    evt = _CALENDAR_STORE[event_id]
    if title:
        evt["title"] = title.strip()
    if start_time:
        evt["start_time"] = start_time.strip()
    if end_time:
        evt["end_time"] = end_time.strip()
    if description is not None:
        evt["description"] = description.strip()
    if location is not None:
        evt["location"] = location.strip()

    return {"success": True, "event": evt}


def calendar_delete(event_id: str) -> Dict[str, Any]:
    """Delete a calendar event by ID.
    
    Args:
        event_id: Event identifier to remove.
    """
    if event_id not in _CALENDAR_STORE:
        return {"error": f"Event ID '{event_id}' not found."}

    deleted = _CALENDAR_STORE.pop(event_id)
    return {"success": True, "deleted_event_id": event_id, "title": deleted["title"]}
