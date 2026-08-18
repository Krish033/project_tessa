import httpx
import re
import json
import urllib.parse
from typing import List, Dict, Any


async def search_youtube(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search YouTube videos for a given query.
    
    Args:
        query: Search query string for YouTube.
        max_results: Maximum videos to return (default: 5).
    """
    if not query or not query.strip():
        return []

    encoded_query = urllib.parse.quote(query.strip())
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()

        html = response.text
        # Locate ytInitialData JSON object in YouTube page HTML
        match = re.search(r"var\s+ytInitialData\s*=\s*({.*?});</script>", html, re.DOTALL)
        if not match:
            match = re.search(r"window\[\"ytInitialData\"\]\s*=\s*({.*?});", html, re.DOTALL)

        videos = []

        if match:
            data = json.loads(match.group(1))
            contents = (
                data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )

            for section in contents:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    if len(videos) >= max_results:
                        break

                    video_renderer = item.get("videoRenderer")
                    if not video_renderer:
                        continue

                    video_id = video_renderer.get("videoId", "")
                    title_runs = video_renderer.get("title", {}).get("runs", [])
                    title = title_runs[0].get("text", "") if title_runs else ""

                    channel_runs = video_renderer.get("ownerText", {}).get("runs", [])
                    channel = channel_runs[0].get("text", "") if channel_runs else ""

                    duration = video_renderer.get("lengthText", {}).get("simpleText", "")
                    views = video_renderer.get("viewCountText", {}).get("simpleText", "")
                    published = video_renderer.get("publishedTimeText", {}).get("simpleText", "")

                    if video_id:
                        videos.append({
                            "title": title,
                            "video_id": video_id,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "channel": channel,
                            "duration": duration,
                            "views": views,
                            "published": published
                        })

        # Fallback parsing with regex if ytInitialData navigation path changed
        if not videos:
            video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":{"runs":\[{"text":"(.*?)"}\]', html)
            seen_ids = set()
            for vid_id, vid_title in video_matches:
                if len(videos) >= max_results:
                    break
                if vid_id not in seen_ids:
                    seen_ids.add(vid_id)
                    videos.append({
                        "title": vid_title,
                        "video_id": vid_id,
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "channel": "",
                        "duration": "",
                        "views": "",
                        "published": ""
                    })

        return videos
    except Exception as e:
        return [{"error": f"Failed to search YouTube: {str(e)}"}]
