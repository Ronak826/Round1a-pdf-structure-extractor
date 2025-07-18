@echo off
echo Running PDF Outline Extractor...
echo.

REM Check if input directory exists
if not exist "input" (
    echo Creating input directory...
    mkdir input
)

REM Check if output directory exists
if not exist "output" (
    echo Creating output directory...
    mkdir output
)

REM Check if there are PDF files in input directory
if not exist "input\*.pdf" (
    echo.
    echo WARNING: No PDF files found in the 'input' directory!
    echo Please place PDF files in the 'input' folder before running.
    echo.
    pause
    exit /b 1
)

echo Processing PDF files...
echo.

REM Run the Docker container
docker run --rm -v "%cd%/input":/app/input -v "%cd%/output":/app/output --network none pdf-outline-extractor:latest

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Processing failed!
    echo Make sure the Docker image is built (run 'build.bat' first).
    pause
    exit /b 1
)

echo.
echo SUCCESS: PDF processing completed!
echo Check the 'output' folder for JSON results.
echo.
pause