

### Project Overview: **Project Tessa** 🤖

**Tessa** is an agentic AI assistant platform designed to move beyond conversational responses by actively planning, executing multi-step tasks using tools, maintaining short- and long-term context/memory, and operating autonomously until goals are completed.

Currently, the repository is structured as a microservices architecture, with the core cognitive engine implemented in `microservices/intelligence`.

---

### High-Level Architecture & Flow

```text
Client / User Request
        ↓
Agent Loop (agent.py)
   ├── Context Manager (Tokenization, Sliding Context, Summaries)
   │     └── Memory Subsystem (Embeddings, STM, LTM via pgvector)
   ├── LLM Driver (Qwen via Ollama)
   ├── Tool Retriever & Registry
   └── Tool Execution & Safety Engine
         ├── Policy & Permission Checks
         ├── Input Validation
         └── Execution (Python tools, OS commands, Web/HTTP, Filesystem)
```

---

### Core Components & Subsystems

#### 1. The Core Agent Loop (`microservices/intelligence/app/agent.py`)
- Drives iterative execution between the user input, LLM reasoning, and tool executions.
- In each cycle:
  1. Compiles context with current conversation, system prompts, active tools, and relevant memory.
  2. Calls the local LLM (`QwenLLM` running via Ollama).
  3. Parses structured responses (`is_final`, `is_tool`, `ltm`).
  4. Automatically stores any extracted long-term memory facts (`ltm`).
  5. Executes requested tools safely, feeds results back as `output`, and continues until a final answer or max iterations is reached.

#### 2. Context & Memory Subsystem (`app/pipeline/context/`)
- **Token Management (`tokenizor.py`)**: Uses HuggingFace tokenizers to track context windows.
- **Summarization (`summerizer.py`)**: Truncates and summarizes long histories to keep token usage within prompt limits.
- **Short-Term & Long-Term Memory (STM & LTM) (`memory/ltm.py`, `embedder.py`)**:
  - Leverages PostgreSQL + `pgvector` for semantic search over historical memory and context.
  - Generates text embeddings for memory extraction and semantic retrieval.
  - Managed via Alembic database migrations (`001` through `005`).

#### 3. Tool Management, Policies & Safety (`app/pipeline/tools/`)
The tool execution layer is modular and enterprise-oriented:
- **Registry & Loader (`registry.py`, `loader.py`)**: Dynamically discovers and registers tools.
- **Retrieval (`retriever.py`)**: Semantically searches relevant tools based on user prompt embeddings.
- **Validation (`validation/`)**: Validates tool arguments against strict schemas before running.
- **Safety & Permissions (`policies/`)**:
  - Enforces permission boundaries and execution policies to prevent dangerous actions (e.g., unauthorized filesystem/system access).
- **Tool Catalog (`meta/definitions/`)**:
  - **Filesystem & System**: File read/write, directory navigation, system statistics, process inspection.
  - **Web & Network**: Web search (`searxng`), URL fetching, weather checking, YouTube metadata.
  - **Productivity & Reminders**: Reminder management, notes, datetime lookups.

#### 4. Tech Stack & Environment
- **Language & Runtime**: Python `^3.14` managed with `uv`.
- **LLM & Inference**: Ollama (`Qwen` model, customized via `Modelfile`).
- **Database & Storage**: PostgreSQL with `SQLAlchemy 2.0`, `pgvector`, and `alembic`.
- **Audio/Speech (Foundational)**: `faster-whisper` and `piper-tts` (for planned voice capabilities).
- **Web/API**: `FastAPI`, `Uvicorn`, `httpx`.
- **Testing**: Comprehensive test suite under `tests/` covering agent loops, context managers, tool permissions, and memory systems.

---

### Current Status
- **Implemented**: Full autonomous agent loop, memory embedding/vector storage, modular tool registry with safety validations, and rich unit/integration tests.
- **Entry Point**: `microservices/intelligence/main.py` provides an executable demonstration running the full pipeline end-to-end.