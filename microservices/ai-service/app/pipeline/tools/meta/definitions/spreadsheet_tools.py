import os
import csv
from typing import Dict, Any, List, Optional, Union


def read_spreadsheet(
    file_path: str,
    max_rows: int = 100,
    delimiter: str = ","
) -> Dict[str, Any]:
    """Read CSV/TSV spreadsheet data into structured rows.
    
    Args:
        file_path: Path to CSV or TSV spreadsheet file.
        max_rows: Maximum rows to read (default: 100).
        delimiter: Column delimiter (default: ',').
    """
    if not file_path or not file_path.strip():
        return {"error": "File path is required."}

    path = os.path.abspath(file_path.strip())
    if not os.path.exists(path):
        return {"error": f"Spreadsheet file not found: '{path}'"}

    if path.endswith(".tsv"):
        delimiter = "\t"

    try:
        rows = []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for idx, row in enumerate(reader):
                if idx >= max_rows:
                    break
                rows.append(row)

        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []

        return {
            "file": path,
            "total_rows": len(rows),
            "headers": headers,
            "rows": data_rows
        }
    except Exception as e:
        return {"error": f"Failed to read spreadsheet: {str(e)}"}


def write_spreadsheet(
    output_path: str,
    rows: List[List[Any]],
    headers: Optional[List[str]] = None,
    delimiter: str = ","
) -> Dict[str, Any]:
    """Write row data to a CSV or TSV spreadsheet file.
    
    Args:
        output_path: Output CSV/TSV file path.
        rows: List of row data lists.
        headers: Optional header row list.
        delimiter: Column delimiter (default: ',').
    """
    if not output_path or not output_path.strip():
        return {"error": "Output path is required."}

    path = os.path.abspath(output_path.strip())
    if path.endswith(".tsv"):
        delimiter = "\t"

    try:
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=delimiter)
            if headers:
                writer.writerow(headers)
            for row in rows:
                writer.writerow(row)

        return {
            "success": True,
            "path": path,
            "row_count": len(rows) + (1 if headers else 0),
            "message": f"Successfully wrote spreadsheet data to '{path}'."
        }
    except Exception as e:
        return {"error": f"Failed to write spreadsheet: {str(e)}"}


def csv_read(file_path: str, max_rows: int = 100) -> Dict[str, Any]:
    """Alias for read_spreadsheet."""
    return read_spreadsheet(file_path, max_rows=max_rows, delimiter=",")


def csv_write(output_path: str, rows: List[List[Any]], headers: Optional[List[str]] = None) -> Dict[str, Any]:
    """Alias for write_spreadsheet."""
    return write_spreadsheet(output_path, rows=rows, headers=headers, delimiter=",")
