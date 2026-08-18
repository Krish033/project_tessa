import httpx
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


async def news_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search news articles using Google News RSS feed.
    
    Args:
        query: News search query string.
        max_results: Maximum news articles to return (default: 5).
    """
    if not query or not query.strip():
        return []

    encoded_query = urllib.parse.quote(query.strip())
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(rss_url, headers=headers)
            response.raise_for_status()

        root = ET.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        articles = []
        for item in channel.findall("item"):
            if len(articles) >= max_results:
                break

            title = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            pub_date = item.findtext("pubDate", default="").strip()
            
            source_elem = item.find("source")
            source_name = source_elem.text.strip() if source_elem is not None and source_elem.text else "Unknown"

            articles.append({
                "title": title,
                "url": link,
                "source": source_name,
                "pub_date": pub_date
            })

        return articles
    except Exception as e:
        return [{"error": f"Failed to search news: {str(e)}"}]
