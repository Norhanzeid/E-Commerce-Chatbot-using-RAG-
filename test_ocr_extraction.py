"""Standalone test: convert a PDF with OCR enabled and inspect the extracted text
before it gets chunked/embedded. Run: python test_ocr_extraction.py
"""
import os
import sys

from ingest import RAW_DATA_DIR, _make_pdf_converter

TEST_PDF = "ShopSphere_FY2025_BI_Report.pdf"
OUTPUT_MD = os.path.join(RAW_DATA_DIR, "ShopSphere_FY2025_BI_Report_ocr_debug.md")


def main():
    pdf_path = os.path.join(RAW_DATA_DIR, TEST_PDF)
    if not os.path.isfile(pdf_path):
        print(f"Test PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"Converting {TEST_PDF} with OCR enabled...")
    converter = _make_pdf_converter()
    result = converter.convert(pdf_path)
    document = result.document

    print(f"Pages detected: {len(document.pages)}")
    print(f"Pictures detected in document: {len(document.pictures)}")
    print(f"Tables detected in document: {len(document.tables)}")

    markdown = document.export_to_markdown()
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Full OCR-merged markdown saved to: {OUTPUT_MD}")

    print("\n--- Preview of extracted text (first 2000 chars) ---")
    print(markdown[:2000])



if __name__ == "__main__":
    main()
