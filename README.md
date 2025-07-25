# 📄 PDF Outline Extractor

A fast, accurate, and offline-capable tool to extract the **title** and **hierarchical headings (H1, H2, H3)** with page numbers from PDF documents, outputting a clean and structured **JSON outline**.

---

## Problem Statement

The goal is to extract a structured, hierarchical outline from PDF documents (up to 50 pages), accurately capturing:

- **Document Title**
- **Headings**: H1, H2, and H3 — with hierarchy and page numbers

This tool is **lightweight**, **fast**, and **self-contained**, capable of running completely **offline**.

---

## Features

-  **Title & Heading Extraction**  
  Detects the main title and heading levels (H1, H2, H3)

-  **Structured JSON Output**  
  Outputs a clean JSON outline with text, level, and page numbers

-  **Offline & Secure**  
  Runs without internet — ensuring full privacy

-  **Optimized for CPU**  
  Compatible with standard `linux/amd64` CPUs — no GPU needed

-  **Dockerized Environment**  
  Fully containerized for consistent and dependency-free execution

- **High Performance**  
  Processes a 50-page PDF in under **10 seconds**

- **Lightweight Footprint**  
  Entire system < **200 MB**

---

##  How It Works: Weighted Scoring System
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

##  Tech Stack

| Component         | Details                          |
|------------------|---------------------------------- |
| **Language**      | Python 3.10+                     |
| **Library Used**  | PyMuPDF (`fitz`)                 |
| **Runtime**       | Dockerized, CPU-only (`amd64`)   |
| **Internet**      | Not Required                     |
| **GPU**           | Not Used                         |
| **Model/Lib Size**| ≤ 200 MB                         |


### 🛠️ Step 1: Build the Docker Image
```bash
- docker build --platform linux/amd64 -t pdfoutlineextractor:round1a .
```

### Step 2: Run the Extractor

```bash
->  docker run --rm \ -v $(pwd)/input:/app/input \ -v $(pwd)/output:/app/output \ --network none \  pdfoutlineextractor:round1a
```

## 📝 Final Notes

- We focused on making the solution as **accurate** and **fast** as possible.
- All logic is **generalized** — nothing is hardcoded for specific files or formats.
- We carefully chose **fast and reliable libraries** after comparing multiple options.
- The codebase is **modular** and designed for easy extension in the next round.
