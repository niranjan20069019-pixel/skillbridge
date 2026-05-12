"""
run.py — Cross-platform launcher for SkillBridge
Works on Windows, Linux, and macOS.
Loads .env, checks YouTube API key, installs deps, starts Flask.
"""
import os
import sys
import platform
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")
ENV_FILE = os.path.join(BASE_DIR, ".env")


# ── Colours (Windows-safe) ────────────────────────────────────────────────────
def supports_colour():
    return sys.stdout.isatty() and platform.system() != "Windows"

G  = "\033[0;32m"  if supports_colour() else ""
Y  = "\033[1;33m"  if supports_colour() else ""
R  = "\033[0;31m"  if supports_colour() else ""
C  = "\033[0;36m"  if supports_colour() else ""
B  = "\033[1m"     if supports_colour() else ""
NC = "\033[0m"     if supports_colour() else ""


def banner():
    print(f"\n{G}{B}{'='*60}{NC}")
    print(f"{G}{B}   SkillBridge — Digital Education & Upskilling Platform{NC}")
    print(f"{G}{B}{'='*60}{NC}\n")


def load_env():
    """Parse .env file and inject into os.environ."""
    if not os.path.exists(ENV_FILE):
        print(f"{Y}[WARN]{NC} No .env file found.")
        print(f"       Copy .env.example to .env and add your YOUTUBE_API_KEY.")
        print()
        return

    print(f"{C}[INFO]{NC} Loading environment from .env ...")
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key   = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:   # don't override real env vars
                    os.environ[key] = value
    print(f"{G}[OK]{NC}   .env loaded.")


def check_youtube_api():
    """Report whether the YouTube API key is configured."""
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if key:
        print(f"{G}[OK]{NC}   YouTube API key found — live video search {G}ENABLED{NC}.")
    else:
        print(f"{Y}[INFO]{NC} No YOUTUBE_API_KEY set — using curated fallback videos.")
        print(f"       To enable live search: add YOUTUBE_API_KEY=<your_key> to .env")
    print()


def detect_os():
    system = platform.system()
    print(f"{C}[INFO]{NC} Detected OS: {system} ({platform.release()})")
    return system


def get_python_executable():
    system = detect_os()
    if system == "Windows":
        candidates = [
            os.path.join(VENV_DIR, "Scripts", "python.exe"),
            "python",
            "python3",
            "py",
        ]
    else:
        candidates = [
            os.path.join(VENV_DIR, "bin", "python"),
            "python3",
            "python",
        ]
    for py in candidates:
        try:
            result = subprocess.run(
                [py, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                ver = result.stdout.strip() or result.stderr.strip()
                print(f"{G}[OK]{NC}   Using Python: {py}  ({ver})")
                return py
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    print(f"{R}[ERROR]{NC} Python 3.8+ not found.")
    print("        Install from https://python.org and ensure it's on your PATH.")
    sys.exit(1)


def install_requirements(python_exe):
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    if not os.path.exists(req_file):
        print(f"{R}[ERROR]{NC} requirements.txt not found!")
        sys.exit(1)
    print(f"{C}[INFO]{NC} Installing / verifying dependencies ...")
    subprocess.run(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
        check=True,
    )
    subprocess.run(
        [python_exe, "-m", "pip", "install", "-r", req_file, "--quiet"],
        check=True,
    )
    print(f"{G}[OK]{NC}   Dependencies ready.")


def ensure_instance_dir():
    instance_dir = os.path.join(BASE_DIR, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    print(f"{G}[OK]{NC}   Instance directory ready.")


def launch_server(python_exe):
    app_file = os.path.join(BASE_DIR, "app.py")
    print(f"\n{G}{B}{'='*60}{NC}")
    print(f"{G}{B}   Server starting at: http://localhost:5000{NC}")
    print(f"{G}{B}   Open your browser and go to the URL above.{NC}")
    print(f"{G}{B}   Press CTRL+C to stop the server.{NC}")
    print(f"{G}{B}{'='*60}{NC}\n")

    env = os.environ.copy()
    env["FLASK_ENV"] = "development"
    env["PYTHONPATH"] = BASE_DIR
    subprocess.run([python_exe, app_file], env=env)


if __name__ == "__main__":
    banner()
    load_env()
    check_youtube_api()
    python_exe = get_python_executable()
    install_requirements(python_exe)
    ensure_instance_dir()
    launch_server(python_exe)
