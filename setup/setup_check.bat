@echo off
echo Running IIT BHU Workshop Setup Check...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo The setup script needs Python to run, but the workshop itself only requires Docker.
    echo Install Python 3.11+ or verify Docker manually: docker compose version
    pause
    exit /b 1
)

cd /d "%~dp0"
python setup_check.py

set EXIT_CODE=%errorlevel%
echo.
if %EXIT_CODE% neq 0 (
    echo Setup check completed with errors. Please review the output above.
) else (
    echo Setup check completed successfully!
)
pause
exit /b %EXIT_CODE%
