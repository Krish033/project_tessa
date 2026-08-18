import subprocess
from typing import Dict, Any, List, Optional


def git(subcommand: str, args: Optional[List[str]] = None, cwd: str = ".") -> Dict[str, Any]:
    """Execute safe git subcommands (e.g. status, log, diff, branch, commit, checkout).
    
    Args:
        subcommand: Git subcommand (e.g. 'status', 'diff', 'log', 'branch').
        args: Optional list of command arguments/flags.
        cwd: Working directory (default: '.').
    """
    if not subcommand or not subcommand.strip():
        return {"error": "Git subcommand is required."}

    sub = subcommand.strip()
    cmd = ["git", sub] + (args if args else [])

    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = res.stdout
        if res.stderr:
            output += f"\n[STDERR]\n{res.stderr}"

        return {
            "success": res.returncode == 0,
            "exit_code": res.returncode,
            "subcommand": sub,
            "output": output.strip() or "Git command executed cleanly (no output)."
        }
    except Exception as e:
        return {"error": f"Failed to execute git command: {str(e)}"}
