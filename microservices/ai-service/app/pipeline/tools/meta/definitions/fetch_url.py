import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, Any


async def fetch_url(url: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Fetch a webpage URL and extract clean body text content.
    
    Args:
        url: The web URL to fetch.
        max_chars: Maximum characters of extracted text to return (default: 4000).
    """
    if not url or not url.strip():
        return {"error": "URL cannot be empty."}

    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        
        # If response is plain text / JSON, return directly
        if "text/plain" in content_type or "application/json" in content_type:
            text = response.text
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[... TRUNCATED ...]"
            return {
                "url": str(response.url),
                "status_code": response.status_code,
                "title": "",
                "content": text
            }

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title_elem = soup.find("title")
        title = title_elem.get_text(strip=True) if title_elem else ""

        # Remove non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg", "noscript"]):
            tag.decompose()

        # Extract main text
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "\n\n[... TRUNCATED ...]"

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "title": title,
            "content": clean_text
        }
    except Exception as e:
        return {
            "url": url,
            "error": f"Failed to fetch URL: {str(e)}"
        }
