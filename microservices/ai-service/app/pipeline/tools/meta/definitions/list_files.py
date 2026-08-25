import os
import fnmatch
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


def list_files(
    directory_path: str = ".",
    pattern: Optional[str] = None,
    recursive: bool = True,
    sort_by: str = "modified",
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """List and inspect files in a directory with file sizes, modified timestamps, and sorting.
    
    Args:
        directory_path: Path to directory to inspect (default: '.').
        pattern: Optional filename or extension pattern to filter (e.g. '*.py', '*.json').
        recursive: Whether to scan subdirectories recursively (default: True).
        sort_by: How to sort files: 'modified' (newest first), 'size' (largest first), 'name' (A-Z).
        max_results: Maximum files to return (default: 20).
    """
    clean_path = directory_path.strip() if directory_path else "."
    root_path = os.path.abspath(clean_path)

    if not os.path.exists(root_path):
        return [{"error": f"Directory not found: '{root_path}'"}]

    if not os.path.isdir(root_path):
        return [{"error": f"Path is not a directory: '{root_path}'"}]

    collected_files = []

    # Ignored directories
    ignored_dirs = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", ".idea", ".vscode"}

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in ignored_dirs]

            for fname in filenames:
                if pattern and not fnmatch.fnmatch(fname.lower(), pattern.lower()):
                    continue

                full_path = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(full_path)
                    mod_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                    rel_path = os.path.relpath(full_path, root_path)
                    collected_files.append({
                        "file_name": fname,
                        "relative_path": rel_path.replace("\\", "/"),
                        "size_bytes": stat.st_size,
                        "size_kb": round(stat.st_size / 1024, 2),
                        "modified": mod_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "mtime": stat.st_mtime,
                    })
                except Exception:
                    continue
    else:
        try:
            for fname in os.listdir(root_path):
                full_path = os.path.join(root_path, fname)
                if os.path.isdir(full_path):
                    continue
                if pattern and not fnmatch.fnmatch(fname.lower(), pattern.lower()):
                    continue

                try:
                    stat = os.stat(full_path)
                    mod_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                    collected_files.append({
                        "file_name": fname,
                        "relative_path": fname,
                        "size_bytes": stat.st_size,
                        "size_kb": round(stat.st_size / 1024, 2),
                        "modified": mod_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "mtime": stat.st_mtime,
                    })
                except Exception:
                    continue
        except Exception as e:
            return [{"error": f"Failed to list directory '{root_path}': {str(e)}"}]

    # Sort files
    sort_key = sort_by.lower() if sort_by else "modified"
    if sort_key == "size":
        collected_files.sort(key=lambda x: x["size_bytes"], reverse=True)
    elif sort_key == "name":
        collected_files.sort(key=lambda x: x["file_name"].lower())
    else:  # default: modified (newest first)
        collected_files.sort(key=lambda x: x["mtime"], reverse=True)

    # Clean up internal sorting helper before returning
    results = []
    for f in collected_files[:max_results]:
        f_clean = dict(f)
        f_clean.pop("mtime", None)
        results.append(f_clean)

    return results
