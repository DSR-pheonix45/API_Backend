@echo off
REM Windows batch file to start HF DABBY system

echo Starting HF DABBY system...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip packages are installed
echo Checking dependencies...
python -c "import fastapi, uvicorn, celery, redis" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set environment variables
set PYTHONPATH=%cd%

REM Start services based on argument
if "%1"=="dev" (
    echo Starting in development mode...
    python start.py --mode dev
) else if "%1"=="prod" (
    echo Starting in production mode...
    python start.py --mode prod --workers 4
) else if "%1"=="docker" (
    echo Starting with Docker...
    docker-compose up -d
    echo Services started with Docker Compose
    echo Access URLs:
    echo   FastAPI: http://localhost/api/
    echo   Gradio: http://localhost/
    echo   Flower: http://localhost:5555
) else (
    echo Usage: run_app.bat [dev^|prod^|docker]
    echo   dev    - Development mode with auto-reload
    echo   prod   - Production mode with multiple workers
    echo   docker - Start with Docker Compose
    pause
)

pause
