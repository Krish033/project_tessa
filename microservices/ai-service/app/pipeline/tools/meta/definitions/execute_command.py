import shutil
import subprocess
import re

MAX_OUTPUT_CHARS = 2000

# Keywords/patterns forbidden to prevent deletion
FORBIDDEN_PATTERNS = [
    r'\brm\b',
    r'\brmdir\b',
    r'\bunlink\b',
    r'\bshred\b',
    r'\bdd\b',
]

# Interactive commands that hang non-interactive subprocesses
INTERACTIVE_PATTERNS = [
    r'\bnano\b',
    r'\bvim\b',
    r'\bvi\b',
    r'\bemacs\b',
    r'\bsudo\b',
    r'\bless\b',
]

# Shell builtins that won't be found by shutil.which but are always available
SHELL_BUILTINS = {
    "echo", "cd", "pwd", "export", "source", "alias", "unalias",
    "set", "unset", "type", "command", "builtin", "eval", "exec",
    "read", "test", "[", "[[", "if", "then", "else", "fi", "for",
    "while", "do", "done", "case", "esac", "return", "exit",
    "trap", "shift", "wait", "kill", "true", "false", ":", ".",
    "let", "declare", "local", "readonly", "getopts", "printf",
    "umask", "ulimit", "hash", "help", "logout", "times",
}


def _extract_base_command(command: str) -> str | None:
    """Extract the first real command name from a shell command string.
    
    Handles pipes, subshells, env vars, absolute paths, etc.
    Returns None if it can't determine the base command.
    """
    # Strip leading env var assignments (e.g. FOO=bar cmd)
    cmd = command.strip()
    while re.match(r'^[A-Za-z_][A-Za-z0-9_]*=\S*\s+', cmd):
        cmd = re.sub(r'^[A-Za-z_][A-Za-z0-9_]*=\S*\s+', '', cmd, count=1)

    # Get the first token (the actual command)
    parts = cmd.split()
    if not parts:
        return None

    first = parts[0]

    # For absolute/relative paths, extract the basename
    if '/' in first:
        first = first.rsplit('/', 1)[-1]

    return first


def command_exists(command: str) -> bool:
    """Check if the base command in a shell command string is available on the system."""
    base = _extract_base_command(command)
    if not base:
        return False

    # Shell builtins are always available
    if base in SHELL_BUILTINS:
        return True

    # Check if binary exists in PATH
    return shutil.which(base) is not None


def is_deletion_command(command: str) -> bool:
    """Check if command contains forbidden deletion keywords."""
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

def is_interactive_command(command: str) -> bool:
    """Check if command uses interactive editors or sudo."""
    for pattern in INTERACTIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

def _truncate_output(output: str) -> str:
    """Truncate output to MAX_OUTPUT_CHARS, keeping first and last portions."""
    if len(output) <= MAX_OUTPUT_CHARS:
        return output
    half = MAX_OUTPUT_CHARS // 2
    return f"{output[:half]}\n\n[... OUTPUT TRUNCATED ({len(output)} chars total) ...]\n\n{output[-half:]}"

def execute_command(command: str) -> str:
    """Execute a bash shell command safely, with pre-checks for existence, deletion, and interactivity."""
    if is_deletion_command(command):
        return "Error: Deletion commands (e.g., rm, rmdir, unlink) are strictly prohibited."

    if is_interactive_command(command):
        return "Error: Interactive commands (e.g. nano, vim, sudo) are not allowed. Use non-interactive commands like python3 -c, sed, or echo."

    # Pre-check: does the base command exist?
    if not command_exists(command):
        base = _extract_base_command(command) or command
        return f"Error: Command '{base}' not found on this system. [Exit Code: 127]"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[Exit Code: {result.returncode}]"

        output = output.strip() or "Command executed successfully (no output)."
        return _truncate_output(output)
    except Exception as e:
        return f"Error executing command: {e}"
