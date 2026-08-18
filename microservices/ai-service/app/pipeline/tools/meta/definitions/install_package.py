import subprocess
from typing import Dict, Any


def install_package(package_name: str, manager: str = "uv") -> Dict[str, Any]:
    """Install Python packages using package manager (uv or pip).
    
    Args:
        package_name: Name of package to install (e.g. 'requests' or 'numpy').
        manager: Package manager to use ('uv' or 'pip', default: 'uv').
    """
    if not package_name or not package_name.strip():
        return {"error": "Package name is required."}

    pkg = package_name.strip()
    mgr = manager.lower().strip()
    
    if mgr == "uv":
        cmd = ["uv", "pip", "install", pkg]
    else:
        cmd = ["pip", "install", pkg]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = res.stdout
        if res.stderr:
            output += f"\n[STDERR]\n{res.stderr}"

        return {
            "success": res.returncode == 0,
            "exit_code": res.returncode,
            "package": pkg,
            "manager": mgr,
            "output": output.strip()
        }
    except Exception as e:
        return {"error": f"Failed to install package '{pkg}': {str(e)}"}
