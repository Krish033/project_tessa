import sys
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def print_banner(model_name: str = "qwen3:4b"):
    """Render ultra-minimal single line banner."""
    console.print(f"[dim white]ai-service ({model_name})[/dim white]\n")

def print_tool_call(command: str):
    """Render command as a minimal dim shell prompt line."""
    console.print(f"[dim white]$ {command}[/dim white]")

def print_tool_output(output: str):
    """Render command output cleanly indented without panel boxes."""
    if output.strip():
        indented = "\n".join(f"  {line}" for line in output.strip().splitlines())
        console.print(f"[dim white]{indented}[/dim white]\n")

def print_final_response(message: str):
    """Render final response directly without panel borders."""
    md = Markdown(message.strip())
    console.print(md)
    console.print()

def print_error(message: str):
    """Render error inline."""
    console.print(f"[dim white]error: {message}[/dim white]\n")

def print_reasoning_start():
    """Start reasoning display block."""
    sys.stdout.write("\033[96m🧠 [Reasoning] \033[0m")
    sys.stdout.flush()

def print_reasoning_chunk(chunk: str):
    """Stream reasoning chunk in cyan/dim style."""
    sys.stdout.write(f"\033[90m{chunk}\033[0m")
    sys.stdout.flush()

def print_reasoning_end():
    """End reasoning display block."""
    sys.stdout.write("\n\n")
    sys.stdout.flush()

def print_content_start():
    """Start content display block."""
    sys.stdout.write("\033[92m🤖 [Response] \033[0m")
    sys.stdout.flush()

def print_content_chunk(chunk: str):
    """Stream response chunk in standard output."""
    sys.stdout.write(chunk)
    sys.stdout.flush()

def print_content_end():
    """End content display block."""
    sys.stdout.write("\n\n")
    sys.stdout.flush()

