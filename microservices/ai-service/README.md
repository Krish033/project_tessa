Client/App
   ↓
Agent API
   ↓
Agent Orchestrator
   ├── Context Manager
   ├── Tool Retriever
   ├── Qwen
   ├── Tool Executor
   └── Task/Memory Manager
          ↓
   Tool Registry
          ↓
 ┌────────┼────────┐
 Python  HTTP     MCP
 Tools   APIs    Servers