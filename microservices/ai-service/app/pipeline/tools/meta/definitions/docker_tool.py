import subprocess
from typing import Dict, Any, List, Optional


def docker(subcommand: str = "ps", args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Execute Docker CLI subcommands (e.g. ps, images, logs, inspect, stop).
    
    Args:
        subcommand: Docker subcommand (e.g. 'ps', 'images', 'logs').
        args: Optional list of command flags/arguments.
    """
    if not subcommand or not subcommand.strip():
        return {"error": "Docker subcommand is required."}

    sub = subcommand.strip()
    cmd = ["docker", sub] + (args if args else [])

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = res.stdout
        if res.stderr:
            output += f"\n[STDERR]\n{res.stderr}"

        return {
            "success": res.returncode == 0,
            "exit_code": res.returncode,
            "subcommand": sub,
            "output": output.strip()
        }
    except Exception as e:
        return {"error": f"Docker CLI error: {str(e)}"}
