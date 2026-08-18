import os
import re
import subprocess
import shutil
from typing import List, Dict, Any, Optional, Union


def _do_search(
    query: str,
    root_path: str,
    file_pattern: Optional[str] = None,
    is_regex: bool = False,
    max_results: int = 15
) -> List[Dict[str, Any]]:
    matches = []

    # Try using ripgrep (`rg`) if installed
    rg_binary = shutil.which("rg")
    if rg_binary:
        cmd = [rg_binary, "--line-number", "--no-heading", "--color=never", "-i"]
        if not is_regex:
            cmd.append("-F")
        if file_pattern:
            cmd.extend(["-g", file_pattern])
        cmd.extend([query, root_path])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.stdout:
                for line in res.stdout.splitlines():
                    if len(matches) >= max_results:
                        break
                    parts = line.split(":", 2)
                    if len(parts) == 3:
                        matches.append({
                            "file": os.path.relpath(parts[0], root_path),
                            "line_number": int(parts[1]),
                            "line_content": parts[2].strip()
                        })
                return matches
        except Exception:
            pass

    # Python regex fallback traversal
    regex_flags = re.IGNORECASE
    try:
        pattern = query if is_regex else re.escape(query)
        compiled_re = re.compile(pattern, regex_flags)
    except Exception as e:
        return [{"error": f"Invalid regex pattern: {str(e)}"}]

    glob_re = None
    if file_pattern:
        import fnmatch
        glob_re = re.compile(fnmatch.translate(file_pattern), re.IGNORECASE)

    for dirpath, _, filenames in os.walk(root_path):
        if len(matches) >= max_results:
            break
        if ".git" in dirpath or "__pycache__" in dirpath or ".venv" in dirpath:
            continue

        for filename in filenames:
            if len(matches) >= max_results:
                break
            if glob_re and not glob_re.match(filename):
                continue

            full_file_path = os.path.join(dirpath, filename)
            try:
                with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line_str in enumerate(f, start=1):
                        if compiled_re.search(line_str):
                            matches.append({
                                "file": os.path.relpath(full_file_path, root_path),
                                "line_number": line_num,
                                "line_content": line_str.strip()
                            })
                            if len(matches) >= max_results:
                                break
            except Exception:
                continue

    return matches


def search_files(
    query: str,
    search_path: str = ".",
    file_pattern: Optional[str] = None,
    is_regex: bool = False,
    max_results: int = 15
) -> str:
    """Search codebase / directory files for matching text, code identifiers, or regex pattern.
    
    Args:
        query: Search string, keyword, or regex pattern.
        search_path: Path to root directory or file to search (default: '.').
        file_pattern: Optional glob pattern (e.g. '*.py').
        is_regex: Whether query is a regex pattern (default: False).
        max_results: Maximum search match results (default: 15).
    """
    if not query or not query.strip():
        return "No query provided."

    clean_path = search_path.strip() if search_path else "."
    root_path = os.path.abspath(clean_path)
    if not os.path.exists(root_path) or "your/folder" in clean_path.lower() or "path/to" in clean_path.lower():
        root_path = os.path.abspath(".")

    results = _do_search(query.strip(), root_path, file_pattern, is_regex, max_results)

    # Fallback: multi-word keyword search
    if not results and " " in query.strip() and not is_regex:
        stop_words = {"in", "the", "this", "folder", "directory", "find", "all", "get", "main", "calls", "code"}
        words = [w for w in re.split(r'\W+', query.strip()) if len(w) > 2 and w.lower() not in stop_words]
        for word in words:
            word_results = _do_search(word, root_path, file_pattern, is_regex=False, max_results=max_results // max(1, len(words)))
            results.extend(word_results)
            if len(results) >= max_results:
                break

    if not results:
        return f"No matches found for query '{query}' in '{root_path}'."

    formatted_lines = [f"Found {len(results)} match(es) for '{query}':"]
    for r in results:
        if "error" in r:
            return r["error"]
        formatted_lines.append(f"- {r['file']}:{r['line_number']}: {r['line_content']}")

    return "\n".join(formatted_lines)


def search_code(
    query: str,
    search_path: str = ".",
    file_pattern: Optional[str] = None,
    is_regex: bool = False,
    max_results: int = 15
) -> str:
    """Alias for search_files."""
    return search_files(query, search_path, file_pattern, is_regex, max_results)
