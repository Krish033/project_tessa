def format_tool_activity(tool_name: str, arguments: dict) -> str:
    """Format tool call into a concise, human-readable activity status line for CLI."""
    if tool_name in ("web_search", "search_web", "google_search"):
        query = arguments.get("query") or arguments.get("q") or ""
        return f"🔍 Searching the web for '{query}'..." if query else "🔍 Searching the web..."
    elif tool_name in ("news_search", "search_news"):
        query = arguments.get("query") or arguments.get("q") or ""
        return f"📰 Searching news for '{query}'..." if query else "📰 Searching news..."
    elif tool_name in ("get_os_info", "system_info", "get_system_info"):
        return "💻 Checking system information..."
    elif tool_name in ("fetch_url", "read_url", "get_url"):
        url = arguments.get("url") or ""
        return f"🌐 Fetching webpage '{url}'..." if url else "🌐 Fetching webpage..."
    elif tool_name in ("execute_command", "run_command", "bash", "cmd"):
        cmd = arguments.get("command") or arguments.get("cmd") or ""
        return f"⚡ Running command: '{cmd}'..." if cmd else "⚡ Executing command..."
    elif tool_name in ("list_files", "list_directory", "list_dir"):
        path = arguments.get("directory_path") or arguments.get("path") or "."
        pattern = arguments.get("pattern") or ""
        return f"📁 Listing files in '{path}' ({pattern})..." if pattern else f"📁 Listing files in '{path}'..."
    elif tool_name in ("task_list", "list_tasks"):
        return "📋 Checking task list..."
    elif tool_name in ("maps_search", "nearby_places"):
        query = arguments.get("query") or arguments.get("location") or ""
        return f"📍 Looking up location '{query}'..." if query else "📍 Looking up locations..."
    else:
        return f"⚙️ Running {tool_name}..."


# Alias for backward compatibility
_format_tool_activity = format_tool_activity
