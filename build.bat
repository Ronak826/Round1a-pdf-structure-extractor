@echo off
echo Building PDF Outline Extractor Docker Image...
echo.

REM Build the Docker image with AMD64 platform
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker build failed!
    echo Make sure Docker is installed and running.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Docker image built successfully!
echo Image name: pdf-outline-extractor:latest
echo.
echo Next steps:
echo 1. Place PDF files in the 'input' folder
echo 2. Run 'run.bat' to process the PDFs
echo 3. Check the 'output' folder for JSON results
echo.
pause