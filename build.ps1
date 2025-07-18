# PowerShell Build Script for PDF Outline Extractor

Write-Host "Building PDF Outline Extractor Docker Image..." -ForegroundColor Green
Write-Host ""

try {
    # Build the Docker image with AMD64 platform
    Write-Host "Running: docker build --platform linux/amd64 -t pdf-outline-extractor:latest ." -ForegroundColor Yellow
    docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed"
    }
    
    Write-Host ""
    Write-Host "SUCCESS: Docker image built successfully!" -ForegroundColor Green
    Write-Host "Image name: pdf-outline-extractor:latest" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Place PDF files in the 'input' folder"
    Write-Host "2. Run 'run.ps1' to process the PDFs"
    Write-Host "3. Check the 'output' folder for JSON results"
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
    Write-Host "Make sure Docker Desktop is installed and running." -ForegroundColor Red
    Write-Host ""
    exit 1
}

Read-Host "Press Enter to continue..."