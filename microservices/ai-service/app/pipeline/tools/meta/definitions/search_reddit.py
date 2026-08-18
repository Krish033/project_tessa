import httpx
import urllib.parse
from typing import List, Dict, Any, Optional


async def search_reddit(
    query: str,
    subreddit: Optional[str] = None,
    limit: int = 5,
    sort: str = "relevance"
) -> List[Dict[str, Any]]:
    """Search Reddit posts and discussion threads.
    
    Args:
        query: Search query string.
        subreddit: Optional subreddit name to restrict search (e.g. 'python', 'technology').
        limit: Maximum number of posts to retrieve (default: 5).
        sort: Sort order ('relevance', 'hot', 'top', 'new').
    """
    if not query or not query.strip():
        return []

    encoded_query = urllib.parse.quote(query.strip())
    sort_param = sort.lower() if sort.lower() in ("relevance", "hot", "top", "new") else "relevance"
    
    if subreddit and subreddit.strip():
        sub = subreddit.strip().lstrip("r/").strip()
        url = f"https://www.reddit.com/r/{sub}/search.json?q={encoded_query}&restrict_sr=1&sort={sort_param}&limit={limit}"
    else:
        url = f"https://www.reddit.com/search.json?q={encoded_query}&sort={sort_param}&limit={limit}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TessaAI/1.0"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        data = response.json()
        children = data.get("data", {}).get("children", [])
        
        posts = []
        for child in children:
            post_data = child.get("data", {})
            title = post_data.get("title", "")
            sub_name = post_data.get("subreddit", "")
            score = post_data.get("score", 0)
            num_comments = post_data.get("num_comments", 0)
            author = post_data.get("author", "")
            permalink = post_data.get("permalink", "")
            selftext = post_data.get("selftext", "")
            post_url = f"https://www.reddit.com{permalink}" if permalink else post_data.get("url", "")

            if len(selftext) > 300:
                selftext = selftext[:300] + "..."

            posts.append({
                "title": title,
                "subreddit": f"r/{sub_name}",
                "score": score,
                "num_comments": num_comments,
                "author": author,
                "url": post_url,
                "snippet": selftext
            })

        return posts
    except Exception as e:
        return [{"error": f"Failed to search Reddit: {str(e)}"}]
