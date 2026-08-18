import platform
import subprocess
import os
import shutil


def get_os_info(section: str = "all") -> str:
    """Retrieve detailed OS and hardware specs (OS, CPU, Memory, Disk)."""
    info = []
    sec = section.lower() if section else "all"

    # 1. OS Details
    if sec in ("all", "os"):
        info.append("=== Operating System Info ===")
        info.append(f"System: {platform.system()} {platform.release()}")
        info.append(f"Architecture: {platform.machine()}")
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info.append(f"Distro: {line.split('=')[1].strip().strip('\"')}")
            except Exception:
                pass

    # 2. CPU Details
    if sec in ("all", "cpu", "processor"):
        info.append("\n=== CPU Info ===")
        info.append(f"Processor: {platform.processor() or 'AMD/Intel'}")
        info.append(f"Logical CPUs: {os.cpu_count()}")
        if shutil.which("lscpu"):
            try:
                res = subprocess.run("lscpu | grep 'Model name'", shell=True, capture_output=True, text=True)
                if res.stdout.strip():
                    info.append(res.stdout.strip())
            except Exception:
                pass

    # 3. RAM / Memory Details
    if sec in ("all", "memory", "ram"):
        info.append("\n=== RAM / Memory Info ===")
        if shutil.which("free"):
            try:
                res = subprocess.run("free -h", shell=True, capture_output=True, text=True)
                info.append(res.stdout.strip())
            except Exception:
                pass
        elif os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo") as f:
                    lines = [line.strip() for line in f if "MemTotal" in line or "MemAvailable" in line]
                    info.extend(lines)
            except Exception:
                pass

    # 4. Storage Details
    if sec in ("all", "storage", "disk"):
        info.append("\n=== Storage Info ===")
        if shutil.which("df"):
            try:
                res = subprocess.run("df -h /", shell=True, capture_output=True, text=True)
                info.append(res.stdout.strip())
            except Exception:
                pass

    return "\n".join(info) if info else "No system info available."
