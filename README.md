# 📄 PDF Outline Extractor

A fast, accurate, and offline-capable tool to extract the **title** and **hierarchical headings (H1, H2, H3)** with page numbers from PDF documents, outputting a clean and structured **JSON outline**.

---

## 🎯 Problem Statement

The goal is to extract a structured, hierarchical outline from PDF documents (up to 50 pages), accurately capturing:

- **Document Title**
- **Headings**: H1, H2, and H3 — with hierarchy and page numbers

This tool is **lightweight**, **fast**, and **self-contained**, capable of running completely **offline**.

---

## ✨ Features

- ✅ **Title & Heading Extraction**  
  Detects the main title and heading levels (H1, H2, H3)

- 📦 **Structured JSON Output**  
  Outputs a clean JSON outline with text, level, and page numbers

- 🔐 **Offline & Secure**  
  Runs without internet — ensuring full privacy

- ⚙️ **Optimized for CPU**  
  Compatible with standard `linux/amd64` CPUs — no GPU needed

- 🐳 **Dockerized Environment**  
  Fully containerized for consistent and dependency-free execution

- ⚡ **High Performance**  
  Processes a 50-page PDF in under **10 seconds**

- 🧊 **Lightweight Footprint**  
  Entire system < **200 MB**

---

## ⚙️ How It Works: Weighted Scoring System
We don’t rely on just one thing like font size — instead, we use a Weighted Scoring System to detect heading levels smartly:
To identify headings, the tool uses a **weighted scoring system** based on typography and layout cues:

| Feature            | Weight | Description                                                  |
|--------------------|--------|--------------------------------------------------------------|
| **Font Size**      | 35%    | Scored relative to the document’s median font size          |
| **Bold Detection** | 25%    | Detects bold or semi-bold font weight                       |
| **Positioning**    | 15%    | Analyzes left-alignment and vertical spacing                |
| **Pattern Matching** | 15%  | Recognizes common numbering patterns (e.g., 1., 1.1, A.)     |
| **Length Check**   | 10%    | Filters out unusually short or long candidates              |

This multi-factor method ensures **high precision and recall** across diverse PDF styles.

---


### 🛠️ Step 1: Build the Docker Image


docker build --platform linux/amd64 -t pdfoutlineextractor:round1a .


Step 3: Run the Extractor
docker run --rm \ -v $(pwd)/input:/app/input \ -v $(pwd)/output:/app/output \ --network none \ pdfoutlineextractor:round1a

Example JSON Output

{
  "title": "Sample PDF Title",
  "headings": [
    { "level": "H1", "text": "1. Introduction", "page": 1 },
    { "level": "H2", "text": "1.1 Background", "page": 2 },
    { "level": "H2", "text": "1.2 Purpose", "page": 2 },
    { "level": "H1", "text": "2. Methodology", "page": 3 },
    { "level": "H3", "text": "2.1.1 Data Sources", "page": 4 }
  ]
}




