#!/bin/bash

echo "Building PDF Outline Extractor Docker Image..."
echo

# Build the Docker image with AMD64 platform
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Docker build failed!"
    echo "Make sure Docker is installed and running."
    exit 1
fi

echo
echo "SUCCESS: Docker image built successfully!"
echo "Image name: pdf-outline-extractor:latest"
echo
echo "Next steps:"
echo "1. Place PDF files in the 'input' folder"
echo "2. Run './run.sh' to process the PDFs"
echo "3. Check the 'output' folder for JSON results"
echo