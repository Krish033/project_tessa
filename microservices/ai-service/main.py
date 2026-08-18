import sys
import uvicorn
from app.api import app

if __name__ == "__main__":
    port = 8000
    host = "0.0.0.0"
    print(f"🚀 Starting Gemini AI Agent Service on http://{host}:{port}")
    print(f"✨ Open http://localhost:{port} in your browser to chat with the agent!")
    uvicorn.run("main:app", host=host, port=port, reload=True)