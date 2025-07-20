FROM --platform=linux/amd64 python:3.11-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY process_pdfs.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Run the script
CMD ["python", "process_pdfs.py"]