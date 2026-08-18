import httpx
import re
import json
import xml.etree.ElementTree as ET
import html
from typing import Dict, Any, List


def _extract_video_id(video_id_or_url: str) -> str:
    s = video_id_or_url.strip()
    if len(s) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', s):
        return s
    
    match = re.search(r'(?:v=|\/([0-9A-Za-z_-]{11})|youtu\.be\/)([0-9A-Za-z_-]{11})', s)
    if match:
        return match.group(2) or match.group(1)
    
    match_fallback = re.search(r'([a-zA-Z0-9_-]{11})', s)
    if match_fallback:
        return match_fallback.group(1)
    
    return s


def _format_timestamp(seconds: float) -> str:
    total_sec = int(seconds)
    mins = total_sec // 60
    secs = total_sec % 60
    hrs = mins // 60
    mins = mins % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


async def youtube_transcript(
    video_id_or_url: str,
    language: str = "en"
) -> Dict[str, Any]:
    """Fetch transcript/subtitles for a YouTube video.
    
    Args:
        video_id_or_url: YouTube video ID or full URL.
        language: Preferred language code (default: 'en').
    """
    if not video_id_or_url or not video_id_or_url.strip():
        return {"error": "video_id_or_url parameter is required."}

    video_id = _extract_video_id(video_id_or_url)
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    
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
            response = await client.get(watch_url, headers=headers)
            response.raise_for_status()

            page_html = response.text
            match = re.search(r"ytInitialPlayerResponse\s*=\s*({.*?});", page_html, re.DOTALL)
            
            caption_tracks = []
            if match:
                player_data = json.loads(match.group(1))
                caption_tracks = (
                    player_data.get("captions", {})
                    .get("playerCaptionsTracklistRenderer", {})
                    .get("captionTracks", [])
                )

            # Fallback regex search for captionTracks if playerResponse path shifted
            if not caption_tracks:
                tracks_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_html, re.DOTALL)
                if tracks_match:
                    caption_tracks = json.loads(tracks_match.group(1))

            if not caption_tracks:
                return {
                    "video_id": video_id,
                    "error": f"No captions/transcripts available for video '{video_id}'."
                }

            # Find matching language track or fallback to first
            target_track = None
            for track in caption_tracks:
                lang_code = track.get("languageCode", "").lower()
                if lang_code == language.lower() or lang_code.startswith(language.lower()):
                    target_track = track
                    break
            
            if not target_track:
                target_track = caption_tracks[0]

            baseUrl = target_track.get("baseUrl")
            if not baseUrl:
                return {"video_id": video_id, "error": "Caption track endpoint missing."}

            # Fetch transcript XML
            xml_response = await client.get(baseUrl, headers=headers)
            xml_response.raise_for_status()

        # Parse XML timedtext
        root = ET.fromstring(xml_response.content)
        segments = []
        full_text_parts = []

        for elem in root.findall("text"):
            start_str = elem.attrib.get("start", "0")
            dur_str = elem.attrib.get("dur", "0")
            text_content = html.unescape(elem.text or "").strip()
            
            if text_content:
                start_sec = float(start_str)
                timestamp_str = _format_timestamp(start_sec)
                segments.append({
                    "start": start_sec,
                    "timestamp": timestamp_str,
                    "text": text_content
                })
                full_text_parts.append(f"[{timestamp_str}] {text_content}")

        formatted_transcript = "\n".join(full_text_parts)

        return {
            "video_id": video_id,
            "language": target_track.get("languageCode", language),
            "segment_count": len(segments),
            "transcript": formatted_transcript,
            "segments": segments[:100]  # sample segments list
        }

    except Exception as e:
        return {
            "video_id": video_id,
            "error": f"Failed to retrieve YouTube transcript: {str(e)}"
        }
