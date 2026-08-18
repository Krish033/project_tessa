import subprocess
from typing import Dict, Any, List, Optional


def run_tests(
    test_path: Optional[str] = None,
    framework: str = "pytest",
    args: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute unit and integration tests using pytest or unittest.
    
    Args:
        test_path: Path to test file or directory.
        framework: 'pytest' or 'unittest' (default: 'pytest').
        args: Optional list of additional flags/arguments.
    """
    cmd = [framework.lower()] if framework.lower() == "pytest" else ["python", "-m", "unittest"]
    
    if test_path:
        cmd.append(test_path)
    if args:
        cmd.extend(args)

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = res.stdout
        if res.stderr:
            output += f"\n[STDERR]\n{res.stderr}"

        return {
            "success": res.returncode == 0,
            "exit_code": res.returncode,
            "framework": framework,
            "output": output.strip()
        }
    except Exception as e:
        return {"error": f"Failed to execute tests: {str(e)}"}
