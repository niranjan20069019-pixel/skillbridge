#!/usr/bin/env bash
# ============================================================
#  SkillBridge — run.sh
#  Cross-platform launcher (Linux / macOS / Git Bash on Windows)
#  Installs deps, loads .env, starts Flask with YouTube API
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colours ──────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}   SkillBridge — Digital Education & Upskilling Platform${NC}"
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo ""

# ── Load .env if present ─────────────────────────────────────
if [ -f ".env" ]; then
    echo -e "${CYAN}[INFO]${NC} Loading environment from .env ..."
    # Export each non-comment, non-empty line
    set -o allexport
    # shellcheck disable=SC1091
    source .env
    set +o allexport
    echo -e "${GREEN}[OK]${NC}   .env loaded."
else
    echo -e "${YELLOW}[WARN]${NC} No .env file found."
    echo -e "       Copy .env.example to .env and add your YOUTUBE_API_KEY for live video search."
    echo ""
fi

# ── Check YouTube API key ─────────────────────────────────────
if [ -n "$YOUTUBE_API_KEY" ]; then
    echo -e "${GREEN}[OK]${NC}   YouTube API key found — live video search ENABLED."
else
    echo -e "${YELLOW}[INFO]${NC} No YOUTUBE_API_KEY set — using curated fallback videos."
    echo -e "       To enable live search: add YOUTUBE_API_KEY=<your_key> to .env"
fi
echo ""

# ── Find Python ───────────────────────────────────────────────
find_python() {
    for cmd in python3 python py; do
        if command -v "$cmd" &>/dev/null; then
            VER=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            MAJOR=$(echo "$VER" | cut -d. -f1)
            MINOR=$(echo "$VER" | cut -d. -f2)
            if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python) || {
    echo -e "${RED}[ERROR]${NC} Python 3.8+ not found."
    echo "        Install from https://python.org and ensure it's on your PATH."
    exit 1
}
echo -e "${GREEN}[OK]${NC}   Python found: $($PYTHON --version)"

# ── Virtual environment (optional but recommended) ────────────
if [ -d "venv" ]; then
    echo -e "${CYAN}[INFO]${NC} Activating existing virtual environment ..."
    # shellcheck disable=SC1091
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
    PYTHON="python"
elif command -v python3 &>/dev/null; then
    echo -e "${CYAN}[INFO]${NC} Creating virtual environment ..."
    $PYTHON -m venv venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
    PYTHON="python"
fi

# ── Install dependencies ──────────────────────────────────────
echo -e "${CYAN}[INFO]${NC} Installing / verifying dependencies ..."
$PYTHON -m pip install --upgrade pip --quiet
$PYTHON -m pip install -r requirements.txt --quiet
echo -e "${GREEN}[OK]${NC}   Dependencies ready."

# ── Create instance directory ─────────────────────────────────
mkdir -p instance
echo -e "${GREEN}[OK]${NC}   Instance directory ready."

# ── Launch ────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}   Server starting at: http://localhost:5000${NC}"
echo -e "${GREEN}${BOLD}   Open your browser and go to the URL above.${NC}"
echo -e "${GREEN}${BOLD}   Press CTRL+C to stop the server.${NC}"
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo ""

export FLASK_ENV=development
export PYTHONPATH="$SCRIPT_DIR"

$PYTHON app.py
