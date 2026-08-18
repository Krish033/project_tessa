import httpx
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


async def _search_arxiv(query: str, max_results: int) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query.strip())
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()

    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip().replace("\n", " ")
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip().replace("\n", " ")
        published = entry.findtext("atom:published", default="", namespaces=ns).strip()
        entry_id = entry.findtext("atom:id", default="", namespaces=ns).strip()

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.findtext("atom:name", default="", namespaces=ns)
            if name:
                authors.append(name.strip())

        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break

        papers.append({
            "title": title,
            "authors": authors,
            "summary": summary,
            "published": published,
            "url": entry_id,
            "pdf_url": pdf_url,
            "source": "arXiv"
        })

    return papers


async def _search_semantic_scholar(query: str, max_results: int) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={max_results}&fields=title,authors,abstract,url,year,citationCount"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()

    data = response.json()
    papers = []
    for item in data.get("data", []):
        authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]
        papers.append({
            "title": item.get("title", ""),
            "authors": authors,
            "summary": item.get("abstract") or "",
            "published": str(item.get("year", "")),
            "url": item.get("url") or "",
            "citations": item.get("citationCount", 0),
            "source": "Semantic Scholar"
        })

    return papers


async def search_academic(
    query: str,
    max_results: int = 5,
    source: str = "arxiv"
) -> List[Dict[str, Any]]:
    """Search academic research papers from arXiv or Semantic Scholar.
    
    Args:
        query: Research query topic or keywords.
        max_results: Maximum paper results to return (default: 5).
        source: 'arxiv' (default) or 'semantic_scholar'.
    """
    if not query or not query.strip():
        return []

    try:
        if source.lower() == "semantic_scholar":
            return await _search_semantic_scholar(query, max_results)
        else:
            return await _search_arxiv(query, max_results)
    except Exception as e:
        # Fallback to alternative source if primary fails
        try:
            if source.lower() == "semantic_scholar":
                return await _search_arxiv(query, max_results)
            else:
                return await _search_semantic_scholar(query, max_results)
        except Exception:
            return [{"error": f"Failed to search academic papers: {str(e)}"}]
