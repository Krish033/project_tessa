import httpx
import json
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from app.core.database import db_session
from app.pipeline.context.memory.embedder import Embedder
from app.pipeline.tools.meta.retriever import ToolRetriever


def sql_query(query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a safe SQL query against PostgreSQL database session.
    
    Args:
        query: SQL SELECT query string.
        params: Optional dictionary of query parameters.
    """
    if not query or not query.strip():
        return {"error": "SQL query cannot be empty."}

    q = query.strip()
    if not q.lower().startswith("select"):
        return {"error": "Only SELECT SQL queries are allowed."}

    try:
        with db_session() as db:
            result = db.execute(text(q), params or {})
            keys = list(result.keys()) if hasattr(result, "keys") else []
            rows = [dict(zip(keys, row)) for row in result.fetchall()]

        return {
            "query": q,
            "row_count": len(rows),
            "columns": keys,
            "rows": rows
        }
    except Exception as e:
        return {"error": f"SQL execution error: {str(e)}"}


def vector_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Perform vector embedding similarity search over PostgreSQL database.
    
    Args:
        query: Text search query.
        top_k: Number of nearest vector matches to retrieve (default: 5).
    """
    if not query or not query.strip():
        return []

    try:
        retriever = ToolRetriever()
        return retriever.retrieve(query, top_k=top_k)
    except Exception as e:
        return [{"error": f"Vector search error: {str(e)}"}]


async def api_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Make HTTP API requests (GET, POST, PUT, DELETE) with headers and JSON body.
    
    Args:
        url: Endpoint URL.
        method: HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        headers: Optional HTTP headers dictionary.
        json_body: Optional JSON payload dictionary.
        params: Optional query parameters dictionary.
    """
    if not url or not url.strip():
        return {"error": "API request URL is required."}

    target_url = url.strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = "https://" + target_url

    m = method.upper().strip()

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.request(
                method=m,
                url=target_url,
                headers=headers,
                json=json_body,
                params=params
            )

        content_type = resp.headers.get("content-type", "").lower()
        res_payload: Any = resp.text
        if "application/json" in content_type:
            try:
                res_payload = resp.json()
            except Exception:
                pass

        return {
            "url": str(resp.url),
            "status_code": resp.status_code,
            "method": m,
            "data": res_payload
        }
    except Exception as e:
        return {"error": f"API request error: {str(e)}"}


def json_transform(data: Any, key_path: Optional[str] = None) -> Any:
    """Transform or extract nested keys from a JSON dictionary or array.
    
    Args:
        data: JSON object, dictionary, array, or JSON string.
        key_path: Dot-separated nested key path (e.g. 'users.0.name').
    """
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
        except Exception:
            parsed = data
    else:
        parsed = data

    if not key_path:
        return parsed

    current = parsed
    for key in key_path.strip().split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None

    return current
