import subprocess
import shutil
from typing import Dict, Any


def send_notification(
    title: str,
    message: str,
    level: str = "info"
) -> Dict[str, Any]:
    """Send a system / desktop notification.
    
    Args:
        title: Notification title string.
        message: Notification body message text.
        level: Priority level ('info', 'warning', 'error').
    """
    if not title or not title.strip():
        return {"error": "Title parameter is required."}

    # Try notify-send on Linux if available
    notify_send = shutil.which("notify-send")
    if notify_send:
        try:
            urgency = "critical" if level == "error" else "normal"
            subprocess.run([notify_send, "-u", urgency, title.strip(), message.strip()], capture_output=True, timeout=5)
        except Exception:
            pass

    return {
        "success": True,
        "title": title.strip(),
        "message": message.strip(),
        "level": level
    }
