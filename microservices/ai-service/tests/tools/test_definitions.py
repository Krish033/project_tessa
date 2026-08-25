import os
import pytest
from unittest.mock import patch, MagicMock
from app.pipeline.tools.meta.definitions.get_os_info import get_os_info
from app.pipeline.tools.meta.definitions.read_file import read_file
from app.pipeline.tools.meta.definitions.write_file import write_file
from app.pipeline.tools.meta.definitions.edit_file import edit_file
from app.pipeline.tools.meta.definitions.execute_command import execute_command
from app.pipeline.tools.meta.definitions.fetch_url import fetch_url
from app.pipeline.tools.meta.definitions.web_search import web_search


def test_get_os_info():
    info = get_os_info()
    assert "Operating System Info" in info
    assert "CPU Info" in info


def test_file_operations(tmp_path):
    test_file = tmp_path / "sample.txt"

    # Write file
    write_res = write_file(str(test_file), "Hello World\nLine 2\nLine 3")
    assert write_res["success"] is True

    # Read file
    read_res = read_file(str(test_file))
    assert "content" in read_res
    assert "Hello World" in read_res["content"]

    # Edit file
    edit_res = edit_file(str(test_file), "Hello World", "Hi Earth")
    assert edit_res["success"] is True

    # Verify edit
    read_after = read_file(str(test_file))
    assert "Hi Earth" in read_after["content"]


def test_execute_command():
    res = execute_command("echo test")
    assert isinstance(res, str)
    assert "test" in res


@pytest.mark.anyio
@patch("httpx.AsyncClient.get")
async def test_fetch_url(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "text/html"}
    mock_resp.url = "https://example.com"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    res = await fetch_url("https://example.com")
    assert res["status_code"] == 200
    assert "Test content" in res["content"]


@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_web_search(mock_post):
    html_mock = """
    <html><body>
    <div class="result">
        <a class="result__a" href="https://python.org">Python Programming</a>
        <a class="result__snippet">Python is an interpreted language.</a>
        <a class="result__url">https://python.org</a>
    </div>
    </body></html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html_mock
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    res = await web_search("python")
    assert len(res) == 1
    assert res[0]["title"] == "Python Programming"
    assert res[0]["url"] == "https://python.org"


def test_list_files(tmp_path):
    from app.pipeline.tools.meta.definitions.list_files import list_files

    # Create dummy files
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.txt").write_text("text content")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.py").write_text("x = 1\ny = 2\nz = 3\n")

    # List all
    all_files = list_files(str(tmp_path), recursive=True)
    assert len(all_files) == 3

    # Pattern filter
    py_files = list_files(str(tmp_path), pattern="*.py", recursive=True)
    assert len(py_files) == 2
    assert all(f["file_name"].endswith(".py") for f in py_files)

    # Sort by size
    size_sorted = list_files(str(tmp_path), pattern="*.py", sort_by="size")
    assert size_sorted[0]["size_bytes"] >= size_sorted[1]["size_bytes"]
