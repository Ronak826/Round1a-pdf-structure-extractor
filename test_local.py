# test_local.py

import sys
import json
from pathlib import Path

# Import the extractor
from process_pdfs import PDFOutlineExtractor

def test_corrected_extractor():
    """Test the PDF outline extractor"""
    print("🔍 Testing PDF Outline Extractor...")

    # Input and output directories
    input_dir = Path("input")
    output_dir = Path("output")

    # Create directories if they don't exist
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Find all PDFs in input/
    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("⚠️  No PDF files found in input directory")
        print("📝 Please place some PDF files in the 'input' folder and run again")
        return

    # Initialize the extractor
    extractor = PDFOutlineExtractor()

    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file.name}")

        try:
            # Process the PDF to extract title + outline
            result = extractor.process_pdf(str(pdf_file))

            # Create output filename
            output_file = output_dir / f"{pdf_file.stem}_corrected.json"

            # Write result to JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✅ Successfully processed {pdf_file.name}")
            print(f"📄 Title: {result['title']}")
            print(f"📊 Outline entries: {len(result['outline'])}")

            # Example: special check for certain files
            if 'ltc' in pdf_file.name.lower() or 'application' in pdf_file.name.lower():
                print("🔍 Form detected - Expected empty outline")
                if len(result['outline']) == 0:
                    print("✅ CORRECT: Empty outline for form document")
                else:
                    print("❌ INCORRECT: Form should have empty outline")

            print(f"💾 Saved to: {output_file}")

            # Preview first few outline items
            if result['outline']:
                print("📝 Outline preview:")
                for i, heading in enumerate(result['outline'][:5]):
                    print(f"   {heading['level']}: {heading['text']} (page {heading['page']})")
                if len(result['outline']) > 5:
                    print(f"   ... and {len(result['outline']) - 5} more headings")
            else:
                print("📝 No headings found (this is correct for forms)")

        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")

        print("-" * 60)


if __name__ == "__main__":
    test_corrected_extractor()
