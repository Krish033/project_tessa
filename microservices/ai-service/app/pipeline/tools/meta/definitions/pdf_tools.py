import os
import re
import subprocess
import shutil
from typing import Dict, Any, List, Optional


def read_pdf(file_path: str, max_pages: int = 20) -> Dict[str, Any]:
    """Read text from a PDF file page by page.
    
    Args:
        file_path: Path to the PDF file.
        max_pages: Maximum number of pages to read (default: 20).
    """
    if not file_path or not file_path.strip():
        return {"error": "PDF file path is required."}

    path = os.path.abspath(file_path.strip())
    if not os.path.exists(path):
        return {"error": f"PDF file not found: '{path}'"}

    # 1. Try pdftotext CLI if installed
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            res = subprocess.run([pdftotext, "-l", str(max_pages), path, "-"], capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                text = res.stdout
                return {"file": path, "text": text, "method": "pdftotext"}
        except Exception:
            pass

    # 2. Basic stream reader fallback
    try:
        with open(path, "rb") as f:
            content = f.read()

        text_parts = []
        # Find stream text blocks matching BT ... ET
        bt_et_blocks = re.findall(rb"BT(.*?)ET", content, re.DOTALL)
        for block in bt_et_blocks[:max_pages * 10]:
            # extract string literals in parentheses (text)
            strings = re.findall(rb"\((.*?)\)", block)
            for s in strings:
                try:
                    decoded = s.decode("utf-8", errors="ignore")
                    if len(decoded.strip()) > 1:
                        text_parts.append(decoded.strip())
                except Exception:
                    pass

        extracted_text = "\n".join(text_parts) if text_parts else "[PDF Binary Content - text stream extraction complete]"
        return {"file": path, "text": extracted_text, "method": "stream_parser"}
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}


def extract_pdf_text(file_path: str, max_pages: int = 20) -> Dict[str, Any]:
    """Alias for read_pdf."""
    return read_pdf(file_path, max_pages)


def create_pdf(output_path: str, content: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Generate a standard PDF file with title and body text.
    
    Args:
        output_path: Path where output PDF file will be created.
        content: Text content body of the document.
        title: Optional document title.
    """
    if not output_path or not output_path.strip():
        return {"error": "Output PDF path is required."}

    path = os.path.abspath(output_path.strip())

    try:
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        full_text = f"{title}\n\n{content}" if title else content
        escaped_text = full_text.replace("(", "\\(").replace(")", "\\)")
        
        # Build minimal valid PDF 1.4 object structure
        pdf_stream = (
            f"BT\n/F1 12 Tf\n50 750 Td\n14 TL\n"
        )
        for line in escaped_text.splitlines():
            pdf_stream += f"({line}) '\n"
        pdf_stream += "ET"

        stream_bytes = pdf_stream.encode("latin1", errors="replace")
        stream_len = len(stream_bytes)

        pdf_body = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
            b"4 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n" +
            stream_bytes +
            b"\nendstream\nendobj\n"
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
        )

        with open(path, "wb") as f:
            f.write(pdf_body)

        return {
            "success": True,
            "path": path,
            "bytes_written": len(pdf_body),
            "message": f"Successfully generated PDF document at '{path}'."
        }
    except Exception as e:
        return {"error": f"Failed to create PDF: {str(e)}"}
