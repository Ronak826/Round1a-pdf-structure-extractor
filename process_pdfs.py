#!/usr/bin/env python3
"""
Adobe Hackathon Challenge 1A: PDF Outline Extractor
High-performance PDF processing solution for extracting structured outlines
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
import fitz  # PyMuPDF
from statistics import median
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    """
    Advanced PDF outline extraction with multi-criteria heading detection
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the PDF outline extractor with configurable parameters
        
        Args:
            config: Configuration dictionary with extraction parameters
        """
        self.config = config or {
            'font_size_weight': 0.35,
            'bold_weight': 0.25,
            'position_weight': 0.15,
            'pattern_weight': 0.15,
            'length_weight': 0.10,
            'min_heading_score': 0.3,
            'max_heading_length': 200,
            'min_heading_length': 3
        }
        
        # Heading patterns for different levels
        self.heading_patterns = [
            re.compile(r'^\d+\.\s+', re.IGNORECASE),  # H1: "1. Introduction"
            re.compile(r'^\d+\.\d+\s+', re.IGNORECASE),  # H2: "1.1 Background"
            re.compile(r'^\d+\.\d+\.\d+\s+', re.IGNORECASE),  # H3: "1.1.1 Details"
            re.compile(r'^[A-Z][A-Z\s]+$'),  # ALL CAPS headings
            re.compile(r'^(Chapter|Section|Part)\s+\d+', re.IGNORECASE)
        ]
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured outline from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing title and outline structure
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                logger.info(f"Processing PDF: {pdf_path} ({pdf_doc.page_count} pages)")
                
                # Extract title from first page
                title = self._extract_title(pdf_doc)
                
                # Extract headings from all pages
                headings = self._extract_headings(pdf_doc)
                
                # Format output
                outline = {
                    "title": title,
                    "outline": headings
                }
                
                logger.info(f"Extracted {len(headings)} headings from {pdf_path}")
                return outline
                
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            # Return minimal structure for failed processing
            return {
                "title": f"Error processing {Path(pdf_path).stem}",
                "outline": []
            }
    
    def _extract_title(self, pdf_doc: fitz.Document) -> str:
        """
        Extract document title from first page using largest font size
        
        Args:
            pdf_doc: Open PDF document
            
        Returns:
            Extracted title or filename fallback
        """
        try:
            first_page = pdf_doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            title_candidates = []
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if (len(text) > 5 and 
                                len(text) < 150 and 
                                not text.startswith(('http', 'www', '@', '#'))):
                                title_candidates.append({
                                    "text": text,
                                    "size": span["size"],
                                    "flags": span["flags"]
                                })
            
            if title_candidates:
                # Find the largest font size on first page
                max_size = max(candidate["size"] for candidate in title_candidates)
                largest_texts = [c for c in title_candidates if c["size"] == max_size]
                
                if largest_texts:
                    # Prefer the longest text among largest font sizes
                    title = max(largest_texts, key=lambda x: len(x["text"]))["text"]
                    return self._clean_text(title)
            
            # Fallback to document metadata
            metadata = pdf_doc.metadata
            if metadata.get("title"):
                return metadata["title"]
                
        except Exception as e:
            logger.warning(f"Error extracting title: {str(e)}")
        
        return "Document Title"
    
    def _extract_headings(self, pdf_doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract headings using multi-criteria analysis
        
        Args:
            pdf_doc: Open PDF document
            
        Returns:
            List of heading dictionaries with level, text, and page
        """
        all_spans = []
        
        # Extract all text spans with formatting info
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if len(text) >= self.config['min_heading_length']:
                                all_spans.append({
                                    "text": text,
                                    "size": span["size"],
                                    "flags": span["flags"],
                                    "page": page_num + 1,
                                    "bbox": span["bbox"]
                                })
        
        if not all_spans:
            return []
        
        # Calculate median font size for reference
        font_sizes = [span["size"] for span in all_spans]
        median_size = median(font_sizes)
        
        # Score potential headings
        heading_candidates = []
        for span in all_spans:
            score = self._calculate_heading_score(span, median_size)
            if score >= self.config['min_heading_score']:
                heading_candidates.append({
                    "text": span["text"],
                    "page": span["page"],
                    "size": span["size"],
                    "score": score
                })
        
        # Sort by score and assign levels
        heading_candidates.sort(key=lambda x: (-x["score"], x["page"]))
        
        # Assign heading levels based on font size and patterns
        return self._assign_heading_levels(heading_candidates)
    
    def _calculate_heading_score(self, span: Dict, median_size: float) -> float:
        """
        Calculate heading likelihood score using multiple criteria
        
        Args:
            span: Text span with formatting information
            median_size: Median font size in document
            
        Returns:
            Heading score (0-1)
        """
        text = span["text"]
        size = span["size"]
        flags = span["flags"]
        
        # Font size score (relative to median)
        size_score = min(size / median_size, 2.0) / 2.0
        
        # Bold formatting score
        bold_score = 1.0 if flags & 2**4 else 0.0  # Bold flag
        
        # Position score (left-aligned, reasonable y-position)
        pos_score = 0.7  # Simplified position scoring
        
        # Pattern recognition score
        pattern_score = 0.0
        for pattern in self.heading_patterns:
            if pattern.match(text):
                pattern_score = 1.0
                break
        
        # Length score (reasonable heading length)
        length_score = 1.0
        if len(text) > self.config['max_heading_length']:
            length_score = 0.0
        elif len(text) < self.config['min_heading_length']:
            length_score = 0.0
        
        # Calculate weighted score
        total_score = (
            size_score * self.config['font_size_weight'] +
            bold_score * self.config['bold_weight'] +
            pos_score * self.config['position_weight'] +
            pattern_score * self.config['pattern_weight'] +
            length_score * self.config['length_weight']
        )
        
        return min(total_score, 1.0)
    
    def _assign_heading_levels(self, candidates: List[Dict]) -> List[Dict[str, Any]]:
        """
        Assign H1, H2, H3 levels to heading candidates
        
        Args:
            candidates: List of heading candidates with scores
            
        Returns:
            List of formatted headings with levels
        """
        if not candidates:
            return []
        
        # Group by font size
        size_groups = {}
        for candidate in candidates:
            size = round(candidate["size"], 1)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(candidate)
        
        # Sort sizes in descending order
        sorted_sizes = sorted(size_groups.keys(), reverse=True)
        
        # Assign levels based on size ranking
        headings = []
        for i, size in enumerate(sorted_sizes[:3]):  # Only top 3 sizes
            level = f"H{i+1}"
            for candidate in size_groups[size]:
                headings.append({
                    "level": level,
                    "text": self._clean_text(candidate["text"]),
                    "page": candidate["page"]
                })
        
        # Sort by page number
        headings.sort(key=lambda x: x["page"])
        
        return headings
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove common artifacts
        text = re.sub(r'[^\w\s\-.,():\'"!?]', '', text)
        
        return text

def process_pdfs():
    """
    Main function to process all PDFs in input directory
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        return
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Initialize extractor
    extractor = PDFOutlineExtractor()
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Extract outline
            outline = extractor.extract_outline(str(pdf_file))
            
            # Generate output file path
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            # Save JSON output
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved outline to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            
            # Create minimal output for failed files
            error_output = {
                "title": f"Error processing {pdf_file.stem}",
                "outline": []
            }
            
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(error_output, f, indent=2, ensure_ascii=False)
    
    logger.info("Processing complete!")

if __name__ == "__main__":
    process_pdfs()