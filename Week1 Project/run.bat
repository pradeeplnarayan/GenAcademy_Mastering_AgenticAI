@echo off
REM Setup and run script for Body Composition Dashboard (Windows)

echo.
echo 🚀 Body Composition Dashboard Setup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9 or higher.
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Found Python %python_version%
echo.

REM Check if Uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Uv package manager...
    python -m pip install --quiet uv
    if errorlevel 1 (
        echo ❌ Failed to install Uv. Falling back to pip.
        set use_pip=1
    ) else (
        echo ✓ Uv installed successfully
    )
) else (
    echo ✓ Uv is already installed
)

echo.
echo 📥 Installing dependencies...
echo.

if "%use_pip%"=="1" (
    echo Using pip...
    python -m pip install -r requirements.txt
) else (
    echo Using Uv...
    uv sync
)

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully
echo.
echo 🎬 Starting Streamlit app...
echo The app will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

if "%use_pip%"=="1" (
    python -m streamlit run app.py
) else (
    uv run streamlit run app.py
)

pause
