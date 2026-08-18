import asyncio
import os
import sys
from app.pipeline.tools.meta.registry import ToolRegistry
from app.pipeline.tools.loader import load_tools
from app.pipeline.tools.meta.executor import ToolExecutor


def test_tool_registration():
    print("Testing tool registration across all suites...")
    registry = ToolRegistry()
    load_tools(registry, sync_db=False)

    all_tools = registry.get_all()
    tool_names = [t.name for t in all_tools]
    print(f"Total tools registered: {len(tool_names)}")

    expected_tools = [
        # System & Search
        "execute_command", "get_os_info", "web_search", "news_search", "fetch_url", "browser",
        "search_academic", "search_reddit", "search_youtube", "youtube_transcript", "rss_reader",
        # Developer & Files
        "read_file", "write_file", "edit_file", "search_files", "search_code", "git", "github",
        "run_tests", "install_package", "docker",
        # Documents
        "read_pdf", "extract_pdf_text", "create_pdf", "read_docx", "write_docx", "read_spreadsheet",
        "write_spreadsheet", "csv_read", "csv_write", "search_documents",
        # Communication
        "send_email", "read_email", "reply_email", "search_email", "download_attachment",
        "send_message", "read_messages", "send_notification",
        # Productivity
        "calendar_create", "calendar_search", "calendar_update", "calendar_delete",
        "task_create", "task_update", "task_complete", "task_list",
        "notes_create", "notes_search", "notes_update",
        # Maps & Geocoding
        "maps_search", "directions", "nearby_places", "geocode", "reverse_geocode",
        # Data & API
        "sql_query", "vector_search", "api_request", "json_transform"
    ]

    missing = [name for name in expected_tools if not registry.exists(name)]
    assert not missing, f"Missing registered tools: {missing}"
    print(f"✅ Successfully verified all {len(expected_tools)} required tools in ToolRegistry!")


async def test_tool_execution_smoke():
    print("\nRunning smoke execution tests for tool suites...")
    registry = ToolRegistry()
    load_tools(registry, sync_db=False)
    executor = ToolExecutor(registry)

    # 1. Developer File Tools
    test_file = "/tmp/test_tessa_file.txt"
    res_w = await executor.execute("write_file", {"path": test_file, "content": "Hello Tessa World\nLine 2"})
    assert res_w["success"] is True and res_w["result"]["success"] is True
    print("  - write_file: PASSED")

    res_r = await executor.execute("read_file", {"path": test_file})
    assert res_r["success"] is True and "Hello Tessa World" in res_r["result"]["content"]
    print("  - read_file: PASSED")

    res_e = await executor.execute("edit_file", {"path": test_file, "target_content": "Tessa World", "replacement_content": "AI Tools"})
    assert res_e["success"] is True and res_e["result"]["success"] is True
    print("  - edit_file: PASSED")

    res_s = await executor.execute("search_files", {"query": "AI Tools", "search_path": "/tmp"})
    assert res_s["success"] is True
    print("  - search_files: PASSED")

    # 2. Document Tools
    pdf_file = "/tmp/test_doc.pdf"
    res_pdf_c = await executor.execute("create_pdf", {"output_path": pdf_file, "content": "Tessa PDF Test Document"})
    assert res_pdf_c["success"] is True and res_pdf_c["result"]["success"] is True
    print("  - create_pdf: PASSED")

    res_pdf_r = await executor.execute("read_pdf", {"file_path": pdf_file})
    assert res_pdf_r["success"] is True
    print("  - read_pdf: PASSED")

    docx_file = "/tmp/test_doc.docx"
    res_docx_w = await executor.execute("write_docx", {"output_path": docx_file, "content": "Paragraph 1\nParagraph 2"})
    assert res_docx_w["success"] is True and res_docx_w["result"]["success"] is True
    print("  - write_docx: PASSED")

    res_docx_r = await executor.execute("read_docx", {"file_path": docx_file})
    assert res_docx_r["success"] is True and res_docx_r["result"]["paragraph_count"] == 2
    print("  - read_docx: PASSED")

    csv_file = "/tmp/test_data.csv"
    res_csv_w = await executor.execute("write_spreadsheet", {"output_path": csv_file, "headers": ["Name", "Score"], "rows": [["Alice", "95"], ["Bob", "88"]]})
    assert res_csv_w["success"] is True and res_csv_w["result"]["success"] is True
    print("  - write_spreadsheet: PASSED")

    res_csv_r = await executor.execute("read_spreadsheet", {"file_path": csv_file})
    assert res_csv_r["success"] is True and res_csv_r["result"]["total_rows"] == 3
    print("  - read_spreadsheet: PASSED")

    # 3. Communication Tools
    res_email = await executor.execute("send_email", {"to": "test@example.com", "subject": "Hello", "body": "Testing"})
    assert res_email["success"] is True and res_email["result"]["status"] == "sent"
    print("  - send_email: PASSED")

    res_msg = await executor.execute("send_message", {"recipient": "dev_channel", "message": "Deploying tools"})
    assert res_msg["success"] is True and res_msg["result"]["status"] == "sent"
    print("  - send_message: PASSED")

    res_notif = await executor.execute("send_notification", {"title": "Test Title", "message": "Test Message"})
    assert res_notif["success"] is True and res_notif["result"]["success"] is True
    print("  - send_notification: PASSED")

    # 4. Productivity Tools
    res_cal = await executor.execute("calendar_create", {"title": "Team Sync", "start_time": "2026-08-16 10:00", "end_time": "2026-08-16 11:00"})
    assert res_cal["success"] is True and res_cal["result"]["success"] is True
    print("  - calendar_create: PASSED")

    res_task = await executor.execute("task_create", {"title": "Write Unit Tests", "priority": "high"})
    assert res_task["success"] is True and res_task["result"]["success"] is True
    print("  - task_create: PASSED")

    res_note = await executor.execute("notes_create", {"title": "Architecture Notes", "content": "Tool registry details"})
    assert res_note["success"] is True and res_note["result"]["success"] is True
    print("  - notes_create: PASSED")

    # 5. Maps Tools
    res_geo = await executor.execute("geocode", {"address": "Eiffel Tower"})
    assert res_geo["success"] is True
    print("  - geocode: PASSED")

    # 6. Data & API Tools
    res_json = await executor.execute("json_transform", {"data": {"user": {"profile": {"name": "Tessa"}}}, "key_path": "user.profile.name"})
    assert res_json["success"] is True and res_json["result"] == "Tessa"
    print("  - json_transform: PASSED")

    # Cleanup temporary test files
    for p in [test_file, pdf_file, docx_file, csv_file]:
        if os.path.exists(p):
            os.remove(p)

    print("\n🎉 ALL TOOL SUITES TESTED AND PASSED VERIFICATION!")


async def main():
    test_tool_registration()
    await test_tool_execution_smoke()


if __name__ == "__main__":
    asyncio.run(main())
