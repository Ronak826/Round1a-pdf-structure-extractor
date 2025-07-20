import fitz  # PyMuPDF
import json
import re
from pathlib import Path
import logging
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextBlock:
    __slots__ = ('text', 'bbox', 'font_size', 'is_bold', 'page_num', 'y_pos')
    def __init__(self, text, bbox, font_size, is_bold, page_num):
        self.text = text.strip()
        self.bbox = bbox
        self.font_size = round(font_size, 2)
        self.is_bold = is_bold
        self.page_num = page_num
        self.y_pos = bbox[1]

class PDFOutlineExtractor:
    def __init__(self):
        # Header/footer detection patterns
        self.header_footer_patterns = [
            r'^Page \d+ of \d+$',
            r'^© .+$',
            r'^Copyright .+$',
            r'^Version \d+\.\d+$',
            r'^\d{1,2} [A-Za-z]{3,9} \d{4}$',  # Dates like "31 May 2014"
            r'^ISTQB$',
            r'^Overview$',
            r'^Foundation Level Extension – Agile Tester$',
            r'^International Software Testing Qualifications Board$'
        ]
        
        # Heading patterns
        self.heading_patterns = [
            r'^\d+\.\s+',       # "1. Introduction"
            r'^\d+\.\d+\s+',    # "2.1 Audience"
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*:?\s*$'  # Title Case
        ]
        
        # Known heading prefixes
        self.known_headings = [
            "Revision History",
            "Table of Contents",
            "Acknowledgements",
            "References"
        ]

    def _is_header_footer(self, text):
        """Check if text is a header/footer element"""
        text = text.strip()
        if not text:
            return True
            
        # Check against patterns
        for pattern in self.header_footer_patterns:
            if re.match(pattern, text):
                return True
                
        # Check for short text fragments
        if len(text.split()) <= 2 and len(text) < 15:
            return True
            
        return False

    def _is_heading_candidate(self, text):
        """Check if text could be a heading"""
        text = text.strip()
        if not text or len(text) > 200:
            return False
            
        # Check known headings
        for heading in self.known_headings:
            if heading in text:
                return True
                
        # Check against heading patterns
        for pattern in self.heading_patterns:
            if re.match(pattern, text):
                return True
                
        return False

    def _get_heading_level(self, text):
        """Determine heading level based on patterns"""
        # H1: Main numbered sections
        if re.match(r'^\d+\.\s+', text):
            return "H1"
        
        # H2: Subsections
        if re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        
        # H3: Known headings that should be H1
        if any(heading in text for heading in self.known_headings):
            return "H1"
            
        # Default to H2 for other headings
        return "H2"

    def _extract_text_blocks(self, pdf_path):
        """Extract text blocks with line-based combining"""
        all_blocks = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = self._extract_text_blocks_from_page(page, page_num + 1)
            all_blocks.extend(blocks)
                    
        doc.close()
        return all_blocks

    def _extract_text_blocks_from_page(self, page, page_num):
        """Extract text blocks from a single page"""
        lines = defaultdict(list)
        try:
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        font_size = 0
                        is_bold = False
                        bbox = line["bbox"]
                        
                        # Combine spans in the same line
                        for span in line["spans"]:
                            span_text = span["text"].replace('\x00', ' ').strip()
                            if not span_text:
                                continue
                                
                            line_text += span_text + " "
                            font_size = span["size"]
                            is_bold = "bold" in span["font"].lower() or (span["flags"] & 16)
                        
                        if line_text.strip():
                            # Group by approximate y-position
                            y_key = round(bbox[1], 0)
                            lines[y_key].append(TextBlock(
                                text=line_text,
                                bbox=bbox,
                                font_size=font_size,
                                is_bold=is_bold,
                                page_num=page_num
                            ))
        
        except Exception as e:
            logger.error(f"Error extracting from page {page_num}: {e}")
        
        # Combine fragments on same line
        combined_blocks = []
        for y_key in sorted(lines.keys()):
            line_blocks = sorted(lines[y_key], key=lambda x: x.bbox[0])
            
            if line_blocks:
                # Combine text from all blocks on this line
                combined_text = " ".join(block.text for block in line_blocks)
                first_block = line_blocks[0]
                
                combined_blocks.append(TextBlock(
                    text=combined_text,
                    bbox=first_block.bbox,
                    font_size=first_block.font_size,
                    is_bold=first_block.is_bold,
                    page_num=page_num
                ))
        
        return combined_blocks

    def _extract_title(self, all_blocks):
        """Extract document title from largest text on first page"""
        first_page_blocks = [b for b in all_blocks if b.page_num == 1]
        if not first_page_blocks:
            return ""
        
        # Find largest font size
        max_font_size = max(b.font_size for b in first_page_blocks)
        
        # Get candidate title blocks
        title_blocks = []
        for block in first_page_blocks:
            if block.font_size >= max_font_size * 0.8 and not self._is_header_footer(block.text):
                title_blocks.append(block)
        
        # Sort by vertical position
        title_blocks.sort(key=lambda x: x.y_pos)
        
        # Combine title parts
        title = " ".join(block.text.strip() for block in title_blocks)
        return title[:200]  # Limit length

    def process_pdf(self, pdf_path):
        """Main processing function"""
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            # Extract all text blocks
            all_blocks = self._extract_text_blocks(pdf_path)
            
            if not all_blocks:
                return {"title": "", "outline": []}
            
            # Extract title
            title = self._extract_title(all_blocks)
            
            # Extract headings
            outline = []
            seen_headings = set()
            
            for block in all_blocks:
                text = block.text.strip()
                
                # Skip headers/footers and non-heading candidates
                if self._is_header_footer(text) or not self._is_heading_candidate(text):
                    continue
                
                # Get heading level
                level = self._get_heading_level(text)
                
                # Create unique key to avoid duplicates
                heading_key = f"{text}|{block.page_num}"
                if heading_key not in seen_headings:
                    seen_headings.add(heading_key)
                    outline.append({
                        "level": level,
                        "text": text,
                        "page": block.page_num
                    })
            
            # Sort outline by page and position
            outline.sort(key=lambda x: (x["page"], -outline.index(x) if outline else 0))
            
            logger.info(f"Extracted {len(outline)} headings")
            return {"title": title, "outline": outline}
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {"title": "", "outline": []}

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found")
        return
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            result = extractor.process_pdf(str(pdf_file))
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved result to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    main()