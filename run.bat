@echo off
:: ============================================================
:: run.bat — Emotion Recognition Dashboard
:: Supports: Windows 10 / 11
:: Usage: Double-click this file, or run it from a terminal.
:: ============================================================

title Emotion Recognition Dashboard — Launcher
color 0A

echo.
echo  ==========================================
echo   Emotion Recognition Dashboard
echo   Auto-Launcher v1.0
echo  ==========================================
echo.

:: ── STEP 1: Check Python is installed ───────────────────────
echo  [1/4] Checking for Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python was not found on your system.
    echo.
    echo  Please install Python 3.9 or newer from:
    echo  --^> https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check the box that says
    echo  "Add Python to PATH" before clicking Install Now.
    echo.
    echo  After installing, close this window and run this
    echo  script again.
    echo.
    pause
    exit /b 1
)

:: Print the detected Python version for the user's confidence
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo  [OK] Found %PYTHON_VERSION%
echo.

:: ── STEP 2: Check pip is available ──────────────────────────
echo  [2/4] Checking for pip...

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] pip is not available. Try reinstalling Python
    echo  from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  [OK] pip is available.
echo.

:: ── STEP 3: Install / verify dependencies ───────────────────
:: "--quiet" suppresses verbose download logs but still shows errors.
:: "--exists-action i" silently skips packages already installed.
:: This step is safe to run every time — pip is idempotent.
echo  [3/4] Installing / verifying dependencies from requirements.txt...
echo  (This may take a few minutes the first time)
echo.

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Dependency installation failed.
    echo  Check your internet connection and try again.
    echo  If the problem persists, open a terminal and run:
    echo      pip install -r requirements.txt
    echo  to see the full error output.
    echo.
    pause
    exit /b 1
)
echo.
echo  [OK] All dependencies are ready.
echo.

:: ── STEP 4: Launch the Streamlit app ────────────────────────
echo  [4/4] Launching the Emotion Recognition Dashboard...
echo.
echo  The app will open in your default browser automatically.
echo  If it does not, open your browser and go to:
echo  --^> http://localhost:8501
echo.
echo  To stop the app, close this window or press Ctrl+C here.
echo  ==========================================
echo.

:: streamlit run launches a local web server.
:: We pass --server.headless false so the browser opens automatically.
:: --server.port 8501 is the default; explicit here for clarity.
python -m streamlit run app.py ^
    --server.headless false ^
    --server.port 8501 ^
    --browser.gatherUsageStats false

:: If we reach this line, the server was stopped.
echo.
echo  Dashboard stopped. Press any key to close this window.
pause >nul
