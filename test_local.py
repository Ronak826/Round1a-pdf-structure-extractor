#!/usr/bin/env python3
"""
Local test script for PDF Outline Extractor
Run this to test the extraction logic without Docker
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from process_pdfs import PDFOutlineExtractor
    print("✅ Successfully imported PDFOutlineExtractor")
except ImportError as e:
    print(f"❌ Failed to import PDFOutlineExtractor: {e}")
    print("Make sure you have PyMuPDF installed:")
    print("pip install PyMuPDF==1.23.14")
    sys.exit(1)

def test_extractor():
    """Test the PDF extractor with sample data"""
    print("\n🔍 Testing PDF Outline Extractor...")
    
    # Check if input directory exists
    input_dir = Path("input")
    if not input_dir.exists():
        print(f"📁 Creating input directory: {input_dir}")
        input_dir.mkdir()
    
    # Check if output directory exists
    output_dir = Path("output")
    if not output_dir.exists():
        print(f"📁 Creating output directory: {output_dir}")
        output_dir.mkdir()
    
    # Look for PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDF files found in input directory")
        print("📝 Please place some PDF files in the 'input' folder and run again")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Initialize extractor
    extractor = PDFOutlineExtractor()
    
    # Test each PDF
    for pdf_file in pdf_files:
        print(f"\n🔄 Processing: {pdf_file.name}")
        
        try:
            # Extract outline
            outline = extractor.extract_outline(str(pdf_file))
            
            # Print results
            print(f"📋 Title: {outline['title']}")
            print(f"📑 Found {len(outline['outline'])} headings:")
            
            for heading in outline['outline'][:5]:  # Show first 5 headings
                print(f"   {heading['level']}: {heading['text']} (page {heading['page']})")
            
            if len(outline['outline']) > 5:
                print(f"   ... and {len(outline['outline']) - 5} more headings")
            
            # Save to output
            import json
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {str(e)}")
    
    print("\n✅ Local test completed!")
    print("🐳 If everything looks good, you can now use Docker:")
    print("   - Windows: run 'build.bat' then 'run.bat'")
    print("   - Linux/Mac: run './build.sh' then './run.sh'")

if __name__ == "__main__":
    test_extractor()