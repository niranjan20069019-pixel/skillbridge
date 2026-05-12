@echo off
title SkillBridge — Digital Education Platform
color 0A

echo.
echo  ============================================================
echo   SkillBridge — Digital Education ^& Upskilling Platform
echo  ============================================================
echo.

:: ── Load .env if it exists ────────────────────────────────────
if exist ".env" (
    echo  [INFO] Loading environment from .env ...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" (
            if not "%%A"=="" (
                set "%%A=%%B"
            )
        )
    )
    echo  [OK]   .env loaded.
) else (
    echo  [WARN] No .env file found.
    echo         Copy .env.example to .env and add your YOUTUBE_API_KEY for live video search.
    echo.
)

:: ── Check YouTube API key ─────────────────────────────────────
if defined YOUTUBE_API_KEY (
    if not "%YOUTUBE_API_KEY%"=="" (
        echo  [OK]   YouTube API key found -- live video search ENABLED.
    ) else (
        echo  [INFO] No YOUTUBE_API_KEY set -- using curated fallback videos.
    )
) else (
    echo  [INFO] No YOUTUBE_API_KEY set -- using curated fallback videos.
    echo         To enable live search: add YOUTUBE_API_KEY=^<your_key^> to .env
)
echo.

:: ── Check Python ──────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Please install Python 3.8+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('python --version 2^>^&1') do echo  [OK]   %%V found.

:: ── Install dependencies ──────────────────────────────────────
echo  [INFO] Installing / verifying dependencies...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo  [OK]   Dependencies ready.

:: ── Create instance directory ─────────────────────────────────
if not exist "instance" mkdir instance
echo  [OK]   Instance directory ready.

echo.
echo  ============================================================
echo   Server starting at: http://localhost:5000
echo   Open your browser and go to the URL above.
echo   Press CTRL+C to stop the server.
echo  ============================================================
echo.

set FLASK_ENV=development
python app.py

pause
