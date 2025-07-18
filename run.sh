#!/bin/bash

echo "Running PDF Outline Extractor..."
echo

# Check if input directory exists
if [ ! -d "input" ]; then
    echo "Creating input directory..."
    mkdir input
fi

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir output
fi

# Check if there are PDF files in input directory
if [ ! -f input/*.pdf ]; then
    echo
    echo "WARNING: No PDF files found in the 'input' directory!"
    echo "Please place PDF files in the 'input' folder before running."
    echo
    exit 1
fi

echo "Processing PDF files..."
echo

# Run the Docker container
docker run --rm -v "$(pwd)/input":/app/input -v "$(pwd)/output":/app/output --network none pdf-outline-extractor:latest

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Processing failed!"
    echo "Make sure the Docker image is built (run './build.sh' first)."
    exit 1
fi

echo
echo "SUCCESS: PDF processing completed!"
echo "Check the 'output' folder for JSON results."
echo