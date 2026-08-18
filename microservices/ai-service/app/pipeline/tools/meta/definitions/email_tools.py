from typing import Dict, Any, List, Optional


async def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Send an email to a recipient with a subject, body, and optional attachments.
    
    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Message body text.
        attachments: Optional list of attachment file paths.
    """
    if not to or not to.strip():
        return {"error": "Recipient email ('to') is required."}

    return {
        "status": "sent",
        "to": to.strip(),
        "subject": subject,
        "body_length": len(body),
        "attachments": attachments or []
    }


async def read_email(message_id: str) -> Dict[str, Any]:
    """Read full details of an email message by message_id.
    
    Args:
        message_id: Unique email message identifier.
    """
    if not message_id or not message_id.strip():
        return {"error": "message_id is required."}

    return {
        "message_id": message_id.strip(),
        "sender": "example@domain.com",
        "subject": f"Subject for message {message_id}",
        "date": "2026-08-15 10:00:00 UTC",
        "body": f"This is the body content of message {message_id}.",
        "attachments": []
    }


async def reply_email(message_id: str, reply_body: str) -> Dict[str, Any]:
    """Reply to an existing email message.
    
    Args:
        message_id: Original email message_id.
        reply_body: Text content of the reply.
    """
    if not message_id or not message_id.strip():
        return {"error": "message_id is required."}

    return {
        "status": "replied",
        "in_reply_to": message_id.strip(),
        "reply_body": reply_body
    }


async def search_email(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search mailbox messages by sender, subject, or keyword query.
    
    Args:
        query: Search query string.
        max_results: Maximum messages to return (default: 5).
    """
    if not query or not query.strip():
        return []

    return [
        {
            "message_id": f"msg_10{idx}",
            "sender": "support@service.com",
            "subject": f"Re: {query.strip()} update",
            "date": "2026-08-15 09:30:00 UTC",
            "snippet": f"Matching email snippet for {query.strip()}..."
        }
        for idx in range(1, min(max_results, 3) + 1)
    ]


async def download_attachment(message_id: str, attachment_id: str, output_dir: str = ".") -> Dict[str, Any]:
    """Download an email attachment to a local directory.
    
    Args:
        message_id: Email message ID.
        attachment_id: Attachment identifier.
        output_dir: Local directory to save attachment (default: '.').
    """
    return {
        "status": "downloaded",
        "message_id": message_id,
        "attachment_id": attachment_id,
        "saved_path": f"{output_dir}/attachment_{attachment_id}.dat"
    }
