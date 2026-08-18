import uuid
from typing import Dict, Any, List, Optional

_TASK_STORE: Dict[str, Dict[str, Any]] = {}


def task_create(
    title: str,
    due_date: Optional[str] = None,
    priority: str = "medium",
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new task item.
    
    Args:
        title: Task title.
        due_date: Optional due date (YYYY-MM-DD).
        priority: Priority ('low', 'medium', 'high').
        description: Optional description.
    """
    if not title or not title.strip():
        return {"error": "Task title is required."}

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    item = {
        "task_id": task_id,
        "title": title.strip(),
        "status": "pending",
        "priority": priority.lower(),
        "due_date": due_date or "",
        "description": description or ""
    }
    _TASK_STORE[task_id] = item

    return {"success": True, "task": item}


def task_update(
    task_id: str,
    title: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Update details of an existing task item.
    
    Args:
        task_id: Unique task ID.
        title: Optional new title.
        due_date: Optional new due date.
        priority: Optional new priority.
        description: Optional new description.
    """
    if task_id not in _TASK_STORE:
        return {"error": f"Task ID '{task_id}' not found."}

    item = _TASK_STORE[task_id]
    if title:
        item["title"] = title.strip()
    if due_date is not None:
        item["due_date"] = due_date.strip()
    if priority:
        item["priority"] = priority.lower().strip()
    if description is not None:
        item["description"] = description.strip()

    return {"success": True, "task": item}


def task_complete(task_id: str) -> Dict[str, Any]:
    """Mark a task item as completed.
    
    Args:
        task_id: Task identifier.
    """
    if task_id not in _TASK_STORE:
        return {"error": f"Task ID '{task_id}' not found."}

    _TASK_STORE[task_id]["status"] = "completed"
    return {"success": True, "task": _TASK_STORE[task_id]}


def task_list(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all tasks, optionally filtered by status ('pending', 'completed').
    
    Args:
        status_filter: Optional status filter ('pending' or 'completed').
    """
    if not status_filter:
        return list(_TASK_STORE.values())

    sf = status_filter.lower().strip()
    return [t for t in _TASK_STORE.values() if t["status"].lower() == sf]
