import os
from typing import Dict, Any


def edit_file(path: str, target_content: str, replacement_content: str) -> Dict[str, Any]:
    """Edit an existing file by replacing target_content with replacement_content.
    
    Args:
        path: Path to the target file.
        target_content: Exact string substring to be replaced.
        replacement_content: New string content to replace target_content.
    """
    if not path or not path.strip():
        return {"error": "File path cannot be empty."}
    if not target_content:
        return {"error": "target_content cannot be empty."}

    file_path = os.path.abspath(path.strip())

    if not os.path.exists(file_path):
        return {"error": f"File not found: '{file_path}'"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if target_content not in content:
            return {"error": f"target_content not found in file '{file_path}'."}

        occurrences = content.count(target_content)
        new_content = content.replace(target_content, replacement_content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "success": True,
            "path": file_path,
            "replacements": occurrences,
            "message": f"Successfully replaced {occurrences} occurrence(s) of target_content in '{file_path}'."
        }
    except Exception as e:
        return {"error": f"Failed to edit file '{file_path}': {str(e)}"}
