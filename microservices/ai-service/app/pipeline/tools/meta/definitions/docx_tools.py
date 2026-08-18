import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List


def read_docx(file_path: str) -> Dict[str, Any]:
    """Read paragraph text content from Microsoft Word .docx files.
    
    Args:
        file_path: Path to the .docx file.
    """
    if not file_path or not file_path.strip():
        return {"error": "File path is required."}

    path = os.path.abspath(file_path.strip())
    if not os.path.exists(path):
        return {"error": f"DOCX file not found: '{path}'"}

    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                return {"error": "Invalid .docx format: missing word/document.xml"}

            xml_content = zf.read("word/document.xml")

        root = ET.fromstring(xml_content)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        paragraphs = []
        for p in root.findall(".//w:p", ns):
            p_text = "".join([t.text for t in p.findall(".//w:t", ns) if t.text])
            if p_text.strip():
                paragraphs.append(p_text.strip())

        return {
            "file": path,
            "paragraph_count": len(paragraphs),
            "text": "\n\n".join(paragraphs)
        }
    except Exception as e:
        return {"error": f"Failed to read DOCX file: {str(e)}"}


def write_docx(output_path: str, content: str) -> Dict[str, Any]:
    """Create a Word .docx file with formatted paragraph content.
    
    Args:
        output_path: Path where output .docx file will be created.
        content: Text content (paragraphs separated by newlines).
    """
    if not output_path or not output_path.strip():
        return {"error": "Output path is required."}

    path = os.path.abspath(output_path.strip())

    try:
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        
        # Build OpenXML document.xml
        doc_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        doc_xml += '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n<w:body>\n'
        for line in lines:
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            doc_xml += f'<w:p><w:r><w:t>{escaped}</w:t></w:r></w:p>\n'
        doc_xml += '</w:body>\n</w:document>'

        content_types_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
            '<Default Extension="xml" ContentType="application/xml"/>\n'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
            '</Types>'
        )

        rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
            '</Relationships>'
        )

        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml)
            zf.writestr("_rels/.rels", rels_xml)
            zf.writestr("word/document.xml", doc_xml)

        return {
            "success": True,
            "path": path,
            "paragraphs": len(lines),
            "message": f"Successfully created DOCX document at '{path}'."
        }
    except Exception as e:
        return {"error": f"Failed to write DOCX file: {str(e)}"}
