import os
import re
from typing import List, Dict, Any, Optional
from app.pipeline.tools.meta.definitions.pdf_tools import read_pdf
from app.pipeline.tools.meta.definitions.docx_tools import read_docx
from app.pipeline.tools.meta.definitions.spreadsheet_tools import read_spreadsheet


def search_documents(
    query: str,
    directory_path: str = ".",
    file_types: Optional[List[str]] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Scan directory tree for document files (.pdf, .docx, .txt, .md, .csv) and search text content for query.
    
    Args:
        query: Search keyword or term.
        directory_path: Root directory path to search (default: '.').
        file_types: Optional list of file extensions (e.g. ['pdf', 'docx', 'txt']).
        max_results: Maximum search results (default: 20).
    """
    if not query or not query.strip():
        return []

    root_path = os.path.abspath(directory_path.strip())
    if not os.path.exists(root_path):
        return [{"error": f"Directory not found: '{root_path}'"}]

    allowed_exts = set([ext.lower().lstrip(".") for ext in file_types]) if file_types else {"pdf", "docx", "txt", "md", "csv", "tsv"}
    compiled_re = re.compile(re.escape(query.strip()), re.IGNORECASE)

    matches = []

    for dirpath, _, filenames in os.walk(root_path):
        if len(matches) >= max_results:
            break
        if ".git" in dirpath or "__pycache__" in dirpath or ".venv" in dirpath:
            continue

        for filename in filenames:
            if len(matches) >= max_results:
                break

            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext not in allowed_exts:
                continue

            full_path = os.path.join(dirpath, filename)
            doc_text = ""

            try:
                if ext == "pdf":
                    res = read_pdf(full_path, max_pages=10)
                    doc_text = res.get("text", "")
                elif ext == "docx":
                    res = read_docx(full_path)
                    doc_text = res.get("text", "")
                elif ext in ("csv", "tsv"):
                    res = read_spreadsheet(full_path, max_rows=50)
                    rows = res.get("rows", [])
                    doc_text = "\n".join([" ".join(row) for row in rows])
                else:  # txt / md / plain text
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        doc_text = f.read()

                if compiled_re.search(doc_text):
                    # extract snippet context
                    for line_idx, line in enumerate(doc_text.splitlines(), start=1):
                        if compiled_re.search(line):
                            matches.append({
                                "file": full_path,
                                "type": ext,
                                "line_number": line_idx,
                                "snippet": line.strip()
                            })
                            if len(matches) >= max_results:
                                break
            except Exception:
                continue

    return matches
