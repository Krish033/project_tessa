import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any


async def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search the web using DuckDuckGo HTML search and parse top organic results.
    
    Args:
        query: Search term or question.
        max_results: Maximum number of search results to return (default: 5).
    """
    if not query or not query.strip():
        return []

    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    data = {"q": query.strip()}

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result_div in soup.find_all("div", class_="result"):
            if len(results) >= max_results:
                break

            title_elem = result_div.find("a", class_="result__a")
            snippet_elem = result_div.find("a", class_="result__snippet")
            url_elem = result_div.find("a", class_="result__url")

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            link = title_elem.get("href", "")
            
            # Extract actual URL if DDG redirection link is present
            if "/l/?" in link or "uddg=" in link:
                import urllib.parse
                parsed = urllib.parse.urlparse(link)
                qs = urllib.parse.parse_qs(parsed.query)
                if "uddg" in qs:
                    link = qs["uddg"][0]

            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            display_url = url_elem.get_text(strip=True) if url_elem else link

            results.append({
                "title": title,
                "url": link or display_url,
                "snippet": snippet
            })

        return results
    except Exception as e:
        return [{"error": f"Failed to execute web search: {str(e)}"}]
