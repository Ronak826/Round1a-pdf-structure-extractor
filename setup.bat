@echo off
echo.
echo ============================================
echo   PDF Outline Extractor - Setup Script
echo ============================================
echo.

echo Checking system requirements...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is installed and running
echo.

REM Check if Python is installed (for local testing)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Python is not installed (optional for local testing)
    echo You can still use the Docker version
) else (
    echo ✅ Python is installed
)
echo.

echo Project structure:
echo.
echo pdf-outline-extractor/
echo ├── process_pdfs.py      # Main extraction script
echo ├── Dockerfile           # Docker configuration
echo ├── requirements.txt     # Python dependencies
echo ├── build.bat           # Windows build script
echo ├── run.bat             # Windows run script
echo ├── build.sh            # Linux/macOS build script
echo ├── run.sh              # Linux/macOS run script
echo ├── build.ps1           # PowerShell build script
echo ├── run.ps1             # PowerShell run script
echo ├── test_local.py       # Local testing script
echo ├── README.md           # Documentation
echo ├── sample_output.json  # Expected output format
echo ├── input/              # Place PDF files here
echo └── output/             # JSON results appear here
echo.

echo Quick Start Instructions:
echo.
echo 1. BUILD: Run 'build.bat' to build the Docker image
echo 2. INPUT: Place PDF files in the 'input' folder
echo 3. RUN: Run 'run.bat' to process PDFs
echo 4. OUTPUT: Check the 'output' folder for JSON results
echo.

echo Alternative scripts:
echo - For PowerShell users: build.ps1 and run.ps1
echo - For local testing: python test_local.py
echo.

echo Ready to start? Press any key to continue...
pause >nul

echo.
echo Would you like to build the Docker image now? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo.
    echo Building Docker image...
    call build.bat
) else (
    echo.
    echo Setup complete! Run 'build.bat' when ready to build.
)

echo.
echo Setup finished! Check README.md for detailed instructions.
pause