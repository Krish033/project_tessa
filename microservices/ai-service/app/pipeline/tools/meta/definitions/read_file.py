import os
from typing import Dict, Any, Optional


def read_file(
    path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> Dict[str, Any]:
    """Read contents of a file with optional line range slicing.
    
    Args:
        path: Path to the file to read.
        start_line: Optional starting line number (1-indexed).
        end_line: Optional ending line number (1-indexed, inclusive).
    """
    if not path or not path.strip():
        return {"error": "File path cannot be empty."}

    file_path = os.path.abspath(path.strip())

    if not os.path.exists(file_path):
        return {"error": f"File not found: '{file_path}'"}

    if not os.path.isfile(file_path):
        return {"error": f"Path is not a regular file: '{file_path}'"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        s_idx = (start_line - 1) if (start_line and start_line > 0) else 0
        e_idx = end_line if (end_line and end_line > 0) else total_lines

        selected_lines = lines[s_idx:e_idx]

        # Format line-numbered content
        formatted_lines = []
        for idx, line_text in enumerate(selected_lines, start=s_idx + 1):
            formatted_lines.append(f"{idx:4d}: {line_text.rstrip('\r\n')}")

        return {
            "path": file_path,
            "total_lines": total_lines,
            "start_line": s_idx + 1,
            "end_line": min(e_idx, total_lines),
            "content": "\n".join(formatted_lines)
        }
    except Exception as e:
        return {"error": f"Failed to read file '{file_path}': {str(e)}"}
