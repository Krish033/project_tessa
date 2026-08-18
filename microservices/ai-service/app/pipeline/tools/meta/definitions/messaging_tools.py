from typing import Dict, Any, List, Optional


async def send_message(
    recipient: str,
    message: str,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """Send a chat or direct message to a user or channel recipient.
    
    Args:
        recipient: Target user ID, username, or phone/channel.
        message: Message text content.
        channel: Optional channel or platform name (e.g. 'slack', 'discord', 'general').
    """
    if not recipient or not recipient.strip():
        return {"error": "Recipient is required."}

    return {
        "status": "sent",
        "recipient": recipient.strip(),
        "channel": channel or "direct",
        "message_length": len(message)
    }


async def read_messages(
    channel_or_user: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Read recent messages from a channel or user conversation.
    
    Args:
        channel_or_user: Channel name or user identifier.
        limit: Maximum number of messages to retrieve (default: 10).
    """
    if not channel_or_user or not channel_or_user.strip():
        return []

    return [
        {
            "message_id": f"msg_chat_{idx}",
            "sender": "user_alpha",
            "channel": channel_or_user.strip(),
            "timestamp": "2026-08-15T21:00:00Z",
            "content": f"Recent message #{idx} in {channel_or_user.strip()}"
        }
        for idx in range(1, min(limit, 3) + 1)
    ]
