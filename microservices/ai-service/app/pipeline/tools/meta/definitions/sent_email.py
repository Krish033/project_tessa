

async def send_email(
    to: str,
    subject: str,
    body: str,
):
    # actual Gmail API logic
    return {
        "sent": True,
        "to": to,
    }