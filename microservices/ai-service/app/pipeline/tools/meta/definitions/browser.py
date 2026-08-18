import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import urllib.parse


async def browser(
    url: str,
    action: str = "view",
    selector: Optional[str] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """Inspect and interact with web pages (view content, extract links, meta tags, or run CSS selectors).
    
    Args:
        url: Target web page URL.
        action: 'view' (default), 'links', 'extract_meta', or 'query_selector'.
        selector: Optional CSS selector string when action='query_selector'.
        max_results: Maximum extracted links/elements to return (default: 20).
    """
    if not url or not url.strip():
        return {"error": "URL parameter is required."}

    target_url = url.strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = "https://" + target_url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        final_url = str(response.url)
        page_title = soup.find("title").get_text(strip=True) if soup.find("title") else ""

        if action == "links":
            links = []
            for a in soup.find_all("a", href=True):
                if len(links) >= max_results:
                    break
                anchor_text = a.get_text(strip=True)
                href = a["href"].strip()
                if not href or href.startswith("javascript:") or href.startswith("#"):
                    continue
                full_url = urllib.parse.urljoin(final_url, href)
                links.append({"text": anchor_text or "[No Text]", "url": full_url})
            
            return {
                "url": final_url,
                "title": page_title,
                "action": "links",
                "count": len(links),
                "links": links
            }

        elif action == "extract_meta":
            meta_data = {}
            for meta in soup.find_all("meta"):
                name = meta.get("name") or meta.get("property")
                content = meta.get("content")
                if name and content:
                    meta_data[name] = content
            
            return {
                "url": final_url,
                "title": page_title,
                "action": "extract_meta",
                "meta": meta_data
            }

        elif action == "query_selector":
            if not selector:
                return {"error": "CSS 'selector' argument is required for action='query_selector'."}
            
            elements = soup.select(selector)
            results = []
            for el in elements[:max_results]:
                results.append({
                    "tag": el.name,
                    "text": el.get_text(separator=" ", strip=True),
                    "attributes": dict(el.attrs)
                })
            
            return {
                "url": final_url,
                "title": page_title,
                "action": "query_selector",
                "selector": selector,
                "count": len(results),
                "elements": results
            }

        # Default action: "view"
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "svg"]):
            tag.decompose()

        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text:
                headings.append(f"{h.name.upper()}: {text}")

        body_text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        clean_text = "\n".join(lines[:300])  # limit to first 300 lines

        return {
            "url": final_url,
            "title": page_title,
            "action": "view",
            "headings": headings[:15],
            "text": clean_text[:4000]
        }

    except Exception as e:
        return {
            "url": target_url,
            "error": f"Browser tool error: {str(e)}"
        }
