#!/usr/bin/env bash
# ==============================================================
# run.sh — Emotion Recognition Dashboard
# Supports: macOS 12+, Ubuntu 20.04+, Debian-based Linux
# Usage:
#   chmod +x run.sh   (only needed once)
#   ./run.sh
# ==============================================================

set -euo pipefail   

# ── Colour codes for terminal output ──────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}${BOLD} =========================================="
echo -e "  Emotion Recognition Dashboard"
echo -e "  Auto-Launcher v1.0"
echo -e " ==========================================${RESET}"
echo ""

# ── STEP 1: Locate a suitable Python 3 interpreter ────────────
echo -e "${BOLD}[1/4] Checking for Python 3...${RESET}"

# Try python3 first, then fall back to python (some systems alias it)
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)

        # Require Python 3.9 or newer
        if [[ "$MAJOR" -eq 3 && "$MINOR" -ge 9 ]]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo ""
    echo -e "${RED}[ERROR] Python 3.9 or newer was not found on your system.${RESET}"
    echo ""
    echo "  Please install Python from one of the following:"
    echo ""
    echo "  macOS   → https://www.python.org/downloads/macos/"
    echo "            (or via Homebrew: brew install python@3.11)"
    echo ""
    echo "  Ubuntu/Debian → sudo apt update && sudo apt install python3.11"
    echo ""
    echo "  After installing, run this script again."
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK] Found $($PYTHON_CMD --version)${RESET}"
echo ""

# ── STEP 2: Check pip is available ────────────────────────────
echo -e "${BOLD}[2/4] Checking for pip...${RESET}"

if ! "$PYTHON_CMD" -m pip --version &>/dev/null; then
    echo -e "${RED}[ERROR] pip is not available for $PYTHON_CMD.${RESET}"
    echo ""
    echo "  macOS/Linux: try  sudo apt install python3-pip"
    echo "  or visit: https://pip.pypa.io/en/stable/installation/"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK] pip is available.${RESET}"
echo ""

# ── STEP 3: Install / verify dependencies ─────────────────────
echo -e "${BOLD}[3/4] Installing / verifying dependencies...${RESET}"
echo -e "${YELLOW}      (This may take a few minutes the first time)${RESET}"
echo ""

"$PYTHON_CMD" -m pip install --quiet --upgrade pip
"$PYTHON_CMD" -m pip install --quiet -r requirements_rtec.txt

echo -e "${GREEN}[OK] All dependencies are ready.${RESET}"
echo ""

# ── STEP 4: Launch the Streamlit app ──────────────────────────
echo -e "${BOLD}[4/4] Launching the Emotion Recognition Dashboard...${RESET}"
echo ""
echo "  The app will open in your default browser automatically."
echo "  If it does not, open your browser and navigate to:"
echo -e "  ${CYAN}→ http://localhost:8501${RESET}"
echo ""
echo "  Press Ctrl+C in this terminal to stop the server."
echo -e "${BOLD} ==========================================${RESET}"
echo ""

# Disable Streamlit's telemetry prompt and auto-open browser on headless systems
"$PYTHON_CMD" -m streamlit run app.py \
    --server.headless false \
    --server.port 8501 \
    --browser.gatherUsageStats false

echo ""
echo "Dashboard stopped. Goodbye!"
