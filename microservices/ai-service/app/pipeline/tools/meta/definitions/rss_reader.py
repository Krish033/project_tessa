import httpx
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import Dict, Any, List


def _clean_html_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text[:300] + "..." if len(text) > 300 else text


async def rss_reader(feed_url: str, max_items: int = 10) -> Dict[str, Any]:
    """Fetch and parse RSS 2.0 or Atom 1.0 feed from feed_url.
    
    Args:
        feed_url: URL of the RSS or Atom feed.
        max_items: Maximum feed items to return (default: 10).
    """
    if not feed_url or not feed_url.strip():
        return {"error": "feed_url parameter is required."}

    url = feed_url.strip()
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
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        root = ET.fromstring(response.content)
        tag_name = root.tag.lower()

        items = []
        feed_title = ""
        feed_description = ""

        # RSS 2.0 parsing
        if "rss" in tag_name or root.find("channel") is not None:
            channel = root.find("channel")
            if channel is not None:
                feed_title = channel.findtext("title", default="").strip()
                feed_description = channel.findtext("description", default="").strip()

                for item in channel.findall("item"):
                    if len(items) >= max_items:
                        break

                    title = item.findtext("title", default="").strip()
                    link = item.findtext("link", default="").strip()
                    pub_date = item.findtext("pubDate", default="") or item.findtext("dc:date", default="") or ""
                    desc = item.findtext("description", default="") or item.findtext("content:encoded", default="") or ""

                    items.append({
                        "title": title,
                        "link": link,
                        "pub_date": pub_date.strip(),
                        "summary": _clean_html_text(desc)
                    })

        # Atom 1.0 parsing
        elif "feed" in tag_name:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            feed_title = root.findtext("atom:title", default="", namespaces=ns).strip()
            subtitle = root.findtext("atom:subtitle", default="", namespaces=ns).strip()
            feed_description = subtitle

            for entry in root.findall("atom:entry", ns):
                if len(items) >= max_items:
                    break

                title = entry.findtext("atom:title", default="", namespaces=ns).strip()
                updated = entry.findtext("atom:updated", default="", namespaces=ns) or entry.findtext("atom:published", default="", namespaces=ns) or ""
                summary = entry.findtext("atom:summary", default="", namespaces=ns) or entry.findtext("atom:content", default="", namespaces=ns) or ""

                link = ""
                for l in entry.findall("atom:link", ns):
                    if l.attrib.get("rel", "alternate") == "alternate" or not link:
                        link = l.attrib.get("href", "")

                items.append({
                    "title": title,
                    "link": link,
                    "pub_date": updated.strip(),
                    "summary": _clean_html_text(summary)
                })

        return {
            "feed_url": url,
            "feed_title": feed_title,
            "feed_description": feed_description,
            "count": len(items),
            "items": items
        }

    except Exception as e:
        return {
            "feed_url": url,
            "error": f"Failed to fetch or parse RSS feed: {str(e)}"
        }
