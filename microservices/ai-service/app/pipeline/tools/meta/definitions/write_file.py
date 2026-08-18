import os
from typing import Dict, Any


def write_file(path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
    """Write or overwrite text content to a file at path.
    
    Args:
        path: Path to the target file.
        content: Text content to write.
        overwrite: Whether to overwrite existing file (default: True).
    """
    if not path or not path.strip():
        return {"error": "File path cannot be empty."}

    file_path = os.path.abspath(path.strip())

    if os.path.exists(file_path) and not overwrite:
        return {"error": f"File already exists at '{file_path}' and overwrite is False."}

    try:
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "path": file_path,
            "bytes_written": len(content.encode("utf-8")),
            "message": f"Successfully wrote {len(content)} characters to '{file_path}'."
        }
    except Exception as e:
        return {"error": f"Failed to write file '{file_path}': {str(e)}"}
