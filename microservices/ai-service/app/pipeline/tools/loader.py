import uuid
from app.core.database import db_session
from app.models.models import ToolModel
from app.pipeline.memory.embedder import Embedder
from app.pipeline.tools.meta.registry import Tool, ToolRegistry

# Existing / System tools
from app.pipeline.tools.meta.definitions.execute_command import execute_command
from app.pipeline.tools.meta.definitions.sent_email import send_email as sent_email_old
from app.pipeline.tools.meta.definitions.get_os_info import get_os_info

# Search & Media tools
from app.pipeline.tools.meta.definitions.web_search import web_search
from app.pipeline.tools.meta.definitions.news_search import news_search
from app.pipeline.tools.meta.definitions.fetch_url import fetch_url
from app.pipeline.tools.meta.definitions.browser import browser
from app.pipeline.tools.meta.definitions.search_academic import search_academic
from app.pipeline.tools.meta.definitions.search_reddit import search_reddit
from app.pipeline.tools.meta.definitions.search_youtube import search_youtube
from app.pipeline.tools.meta.definitions.youtube_transcript import youtube_transcript
from app.pipeline.tools.meta.definitions.rss_reader import rss_reader

# Developer tools
from app.pipeline.tools.meta.definitions.read_file import read_file
from app.pipeline.tools.meta.definitions.write_file import write_file
from app.pipeline.tools.meta.definitions.edit_file import edit_file
from app.pipeline.tools.meta.definitions.search_files import search_files, search_code
from app.pipeline.tools.meta.definitions.git_tool import git
from app.pipeline.tools.meta.definitions.github_tool import github
from app.pipeline.tools.meta.definitions.run_tests import run_tests
from app.pipeline.tools.meta.definitions.install_package import install_package
from app.pipeline.tools.meta.definitions.docker_tool import docker

# Document Processing tools
from app.pipeline.tools.meta.definitions.pdf_tools import read_pdf, extract_pdf_text, create_pdf
from app.pipeline.tools.meta.definitions.docx_tools import read_docx, write_docx
from app.pipeline.tools.meta.definitions.spreadsheet_tools import read_spreadsheet, write_spreadsheet, csv_read, csv_write
from app.pipeline.tools.meta.definitions.search_documents import search_documents

# Email & Messaging tools
from app.pipeline.tools.meta.definitions.email_tools import send_email, read_email, reply_email, search_email, download_attachment
from app.pipeline.tools.meta.definitions.messaging_tools import send_message, read_messages
from app.pipeline.tools.meta.definitions.notification_tools import send_notification

# Productivity, Calendar, Tasks & Notes tools
from app.pipeline.tools.meta.definitions.calendar_tools import calendar_create, calendar_search, calendar_update, calendar_delete
from app.pipeline.tools.meta.definitions.task_tools import task_create, task_update, task_complete, task_list
from app.pipeline.tools.meta.definitions.notes_tools import notes_create, notes_search, notes_update

# Maps & Geocoding tools
from app.pipeline.tools.meta.definitions.maps_tools import maps_search, directions, nearby_places, geocode, reverse_geocode

# Data & API Integration tools
from app.pipeline.tools.meta.definitions.data_api_tools import sql_query, vector_search, api_request, json_transform


# syncing tools to DB
def sync_tools_to_db(registry: ToolRegistry) -> None:
    embedder = Embedder()

    with db_session() as db:
        for tool in registry.get_all():
            embedding_vector = None
            try:
                text_to_embed = f"Tool: {tool.name}\nDescription: {tool.description}"
                embedding_vector = embedder.embed(text_to_embed)
            except Exception as e:
                print(f"Could not generate embedding for tool '{tool.name}': {e}")

            existing_tool = db.query(ToolModel).filter_by(tool_name=tool.name).first()

            if existing_tool:
                existing_tool.description = tool.description
                existing_tool.parameters = tool.parameters
                existing_tool.permissions = getattr(tool, "permissions", None) or {}
                if embedding_vector is not None:
                    existing_tool.embedding = embedding_vector
            else:
                db_tool = ToolModel(
                    id=uuid.uuid4(),
                    tool_name=tool.name,
                    description=tool.description,
                    embedding=embedding_vector,
                    parameters=tool.parameters,
                    permissions=getattr(tool, "permissions", None) or {},
                )
                db.add(db_tool)


# Loading tools in the registry
def load_tools(registry: ToolRegistry, sync_db: bool = True) -> None:

    def reg(name: str, description: str, function: callable, parameters: dict):
        registry.register(Tool(name=name, description=description, function=function, parameters=parameters))

    # --- System & Execution Tools ---
    reg("execute_command", "Execute a command on the system.", execute_command, {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})
    reg("get_os_info", "Retrieve operating system specs, CPU info, RAM usage, and disk storage details.", get_os_info, {"type": "object", "properties": {"section": {"type": "string"}}, "required": []})

    # --- Search & Web Tools ---
    reg("web_search", "Search the web for a query using search engine results.", web_search, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("news_search", "Search latest news articles for a given query topic.", news_search, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("fetch_url", "Fetch a web page by URL and extract clean readable text content.", fetch_url, {"type": "object", "properties": {"url": {"type": "string"}, "max_chars": {"type": "integer"}}, "required": ["url"]})
    reg("browser", "Inspect web pages, extract interactive hyperlinks, metadata, or query DOM elements via CSS selectors.", browser, {"type": "object", "properties": {"url": {"type": "string"}, "action": {"type": "string"}, "selector": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["url"]})
    reg("search_academic", "Search academic papers and scholarly research from arXiv or Semantic Scholar.", search_academic, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}, "source": {"type": "string"}}, "required": ["query"]})
    reg("search_reddit", "Search Reddit discussion posts and threads.", search_reddit, {"type": "object", "properties": {"query": {"type": "string"}, "subreddit": {"type": "string"}, "limit": {"type": "integer"}, "sort": {"type": "string"}}, "required": ["query"]})
    reg("search_youtube", "Search YouTube videos by query string.", search_youtube, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("youtube_transcript", "Fetch timestamped transcript/subtitles for a YouTube video.", youtube_transcript, {"type": "object", "properties": {"video_id_or_url": {"type": "string"}, "language": {"type": "string"}}, "required": ["video_id_or_url"]})
    reg("rss_reader", "Fetch and parse RSS 2.0 or Atom 1.0 feeds from a feed URL.", rss_reader, {"type": "object", "properties": {"feed_url": {"type": "string"}, "max_items": {"type": "integer"}}, "required": ["feed_url"]})

    # --- Developer & File Tools ---
    reg("read_file", "Read contents of a text file with optional line range slicing.", read_file, {"type": "object", "properties": {"path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}, "required": ["path"]})
    reg("write_file", "Write or overwrite text content to a file at path.", write_file, {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "overwrite": {"type": "boolean"}}, "required": ["path", "content"]})
    reg("edit_file", "Edit an existing file by replacing target_content with replacement_content.", edit_file, {"type": "object", "properties": {"path": {"type": "string"}, "target_content": {"type": "string"}, "replacement_content": {"type": "string"}}, "required": ["path", "target_content", "replacement_content"]})
    reg("search_files", "Search codebase or directory files for matching text, code identifiers, or regex pattern.", search_files, {"type": "object", "properties": {"query": {"type": "string", "description": "Text keyword, variable name, or regex pattern to search (e.g. 'prompt', 'db.query')."}, "search_path": {"type": "string", "description": "Directory path to search. Use '.' for the current folder."}, "file_pattern": {"type": "string"}, "is_regex": {"type": "boolean"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("search_code", "Search codebase or directory files for matching text, code identifiers, or regex pattern.", search_code, {"type": "object", "properties": {"query": {"type": "string", "description": "Text keyword, variable name, or regex pattern to search (e.g. 'prompt', 'db.query')."}, "search_path": {"type": "string", "description": "Directory path to search. Use '.' for the current folder."}, "file_pattern": {"type": "string"}, "is_regex": {"type": "boolean"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("git", "Execute safe git subcommands (e.g. status, log, diff, branch, commit, checkout).", git, {"type": "object", "properties": {"subcommand": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}, "cwd": {"type": "string"}}, "required": ["subcommand"]})
    reg("github", "Interact with GitHub API or gh CLI for issues, pull requests, and repository info.", github, {"type": "object", "properties": {"action": {"type": "string"}, "repo": {"type": "string"}, "number": {"type": "integer"}, "state": {"type": "string"}}, "required": []})
    reg("run_tests", "Execute unit and integration tests using pytest or unittest.", run_tests, {"type": "object", "properties": {"test_path": {"type": "string"}, "framework": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}}, "required": []})
    reg("install_package", "Install Python packages using package manager (uv or pip).", install_package, {"type": "object", "properties": {"package_name": {"type": "string"}, "manager": {"type": "string"}}, "required": ["package_name"]})
    reg("docker", "Execute Docker CLI subcommands (e.g. ps, images, logs, inspect, stop).", docker, {"type": "object", "properties": {"subcommand": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}}, "required": []})

    # --- Document Processing Tools ---
    reg("read_pdf", "Read text from a PDF file page by page.", read_pdf, {"type": "object", "properties": {"file_path": {"type": "string"}, "max_pages": {"type": "integer"}}, "required": ["file_path"]})
    reg("extract_pdf_text", "Extract text from a PDF file page by page.", extract_pdf_text, {"type": "object", "properties": {"file_path": {"type": "string"}, "max_pages": {"type": "integer"}}, "required": ["file_path"]})
    reg("create_pdf", "Generate a standard PDF file with title and body text.", create_pdf, {"type": "object", "properties": {"output_path": {"type": "string"}, "content": {"type": "string"}, "title": {"type": "string"}}, "required": ["output_path", "content"]})
    reg("read_docx", "Read paragraph text content from Microsoft Word .docx files.", read_docx, {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]})
    reg("write_docx", "Create a Word .docx file with formatted paragraph content.", write_docx, {"type": "object", "properties": {"output_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["output_path", "content"]})
    reg("read_spreadsheet", "Read CSV/TSV spreadsheet data into structured rows.", read_spreadsheet, {"type": "object", "properties": {"file_path": {"type": "string"}, "max_rows": {"type": "integer"}, "delimiter": {"type": "string"}}, "required": ["file_path"]})
    reg("write_spreadsheet", "Write row data to a CSV or TSV spreadsheet file.", write_spreadsheet, {"type": "object", "properties": {"output_path": {"type": "string"}, "rows": {"type": "array", "items": {"type": "array"}}, "headers": {"type": "array", "items": {"type": "string"}}, "delimiter": {"type": "string"}}, "required": ["output_path", "rows"]})
    reg("csv_read", "Read CSV file rows.", csv_read, {"type": "object", "properties": {"file_path": {"type": "string"}, "max_rows": {"type": "integer"}}, "required": ["file_path"]})
    reg("csv_write", "Write rows to a CSV file.", csv_write, {"type": "object", "properties": {"output_path": {"type": "string"}, "rows": {"type": "array", "items": {"type": "array"}}, "headers": {"type": "array", "items": {"type": "string"}}}, "required": ["output_path", "rows"]})
    reg("search_documents", "Scan directory tree for document files (.pdf, .docx, .txt, .md, .csv) and search text content for query.", search_documents, {"type": "object", "properties": {"query": {"type": "string"}, "directory_path": {"type": "string"}, "file_types": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer"}}, "required": ["query"]})

    # --- Email & Communication Tools ---
    reg("send_email", "Send an email to a recipient with a subject, body, and optional attachments.", send_email, {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "attachments": {"type": "array", "items": {"type": "string"}}}, "required": ["to", "subject", "body"]})
    reg("read_email", "Read full details of an email message by message_id.", read_email, {"type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]})
    reg("reply_email", "Reply to an existing email message.", reply_email, {"type": "object", "properties": {"message_id": {"type": "string"}, "reply_body": {"type": "string"}}, "required": ["message_id", "reply_body"]})
    reg("search_email", "Search mailbox messages by sender, subject, or keyword query.", search_email, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("download_attachment", "Download an email attachment to a local directory.", download_attachment, {"type": "object", "properties": {"message_id": {"type": "string"}, "attachment_id": {"type": "string"}, "output_dir": {"type": "string"}}, "required": ["message_id", "attachment_id"]})
    reg("send_message", "Send a chat or direct message to a user or channel recipient.", send_message, {"type": "object", "properties": {"recipient": {"type": "string"}, "message": {"type": "string"}, "channel": {"type": "string"}}, "required": ["recipient", "message"]})
    reg("read_messages", "Read recent messages from a channel or user conversation.", read_messages, {"type": "object", "properties": {"channel_or_user": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["channel_or_user"]})
    reg("send_notification", "Send a system / desktop notification.", send_notification, {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}, "level": {"type": "string"}}, "required": ["title", "message"]})

    # --- Productivity, Calendar, Tasks & Notes ---
    reg("calendar_create", "Create a new calendar event.", calendar_create, {"type": "object", "properties": {"title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}, "description": {"type": "string"}, "location": {"type": "string"}}, "required": ["title", "start_time", "end_time"]})
    reg("calendar_search", "Search calendar events by title or keyword.", calendar_search, {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]})
    reg("calendar_update", "Update details of an existing calendar event.", calendar_update, {"type": "object", "properties": {"event_id": {"type": "string"}, "title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}, "description": {"type": "string"}, "location": {"type": "string"}}, "required": ["event_id"]})
    reg("calendar_delete", "Delete a calendar event by ID.", calendar_delete, {"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]})
    reg("task_create", "Create a new task item.", task_create, {"type": "object", "properties": {"title": {"type": "string"}, "due_date": {"type": "string"}, "priority": {"type": "string"}, "description": {"type": "string"}}, "required": ["title"]})
    reg("task_update", "Update details of an existing task item.", task_update, {"type": "object", "properties": {"task_id": {"type": "string"}, "title": {"type": "string"}, "due_date": {"type": "string"}, "priority": {"type": "string"}, "description": {"type": "string"}}, "required": ["task_id"]})
    reg("task_complete", "Mark a task item as completed.", task_complete, {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]})
    reg("task_list", "List all tasks, optionally filtered by status ('pending', 'completed').", task_list, {"type": "object", "properties": {"status_filter": {"type": "string"}}, "required": []})
    reg("notes_create", "Create a new note item.", notes_create, {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}, "required": ["title", "content"]})
    reg("notes_search", "Search notes by title, content, or tag keyword.", notes_search, {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]})
    reg("notes_update", "Update an existing note item.", notes_update, {"type": "object", "properties": {"note_id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}, "required": ["note_id"]})

    # --- Maps & Geocoding ---
    reg("maps_search", "Search map places, addresses, and points of interest.", maps_search, {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]})
    reg("directions", "Calculate routing directions between origin and destination.", directions, {"type": "object", "properties": {"origin": {"type": "string"}, "destination": {"type": "string"}, "mode": {"type": "string"}}, "required": ["origin", "destination"]})
    reg("nearby_places", "Find nearby places of interest (amenities, restaurants, fuel, etc.).", nearby_places, {"type": "object", "properties": {"location": {"type": "string"}, "amenity": {"type": "string"}, "radius_km": {"type": "number"}}, "required": ["location"]})
    reg("geocode", "Convert location address or place name into latitude and longitude coordinates.", geocode, {"type": "object", "properties": {"address": {"type": "string"}}, "required": ["address"]})
    reg("reverse_geocode", "Convert latitude and longitude coordinates into a human-readable address.", reverse_geocode, {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "required": ["latitude", "longitude"]})

    # --- Data & API Integration ---
    reg("sql_query", "Execute a safe SQL SELECT query against database session.", sql_query, {"type": "object", "properties": {"query": {"type": "string"}, "params": {"type": "object"}}, "required": ["query"]})
    reg("vector_search", "Perform vector embedding similarity search over PostgreSQL database.", vector_search, {"type": "object", "properties": {"query": {"type": "string"}, "top_k": {"type": "integer"}}, "required": ["query"]})
    reg("api_request", "Make HTTP API requests (GET, POST, PUT, DELETE) with headers and JSON body.", api_request, {"type": "object", "properties": {"url": {"type": "string"}, "method": {"type": "string"}, "headers": {"type": "object"}, "json_body": {"type": "object"}, "params": {"type": "object"}}, "required": ["url"]})
    reg("json_transform", "Transform or extract nested keys from a JSON dictionary or array.", json_transform, {"type": "object", "properties": {"data": {}, "key_path": {"type": "string"}}, "required": ["data"]})

    # Persist registered tools to PostgreSQL DB
    if sync_db:
        try:
            sync_tools_to_db(registry)
        except Exception as e:
            print(f"Could not sync tools to DB: {e}")