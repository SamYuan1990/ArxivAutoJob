"""
A safe PDF to Markdown converter that runs in a separate process
to isolate potential crashes from the MuPDF library.
"""

import sys
import logging
import pymupdf4llm
import pymupdf

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert(pdf_path: str):
    """Converts a PDF to Markdown and prints to stdout."""
    try:
        # First, try the primary conversion method
        markdown_output = pymupdf4llm.to_markdown(pdf_path, show_progress=False)
        print(markdown_output)
    except Exception as e:
        logger.error(f"[safe_converter] pymupdf4llm failed for {pdf_path}: {e}")
        # If it fails, attempt the fallback text extraction
        try:
            doc = pymupdf.open(pdf_path)
            text_content = "".join(page.get_text() for page in doc)
            doc.close()
            print(text_content) # Print raw text as fallback
            logger.info(f"[safe_converter] Fallback to text extraction succeeded for {pdf_path}")
        except Exception as fallback_e:
            logger.critical(f"[safe_converter] Fallback text extraction also failed for {pdf_path}: {fallback_e}")
            # Exit with a non-zero code to indicate failure to the parent process
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python safe_converter.py <path_to_pdf_file>", file=sys.stderr)
        sys.exit(1)
    
    pdf_file_path = sys.argv[1]
    convert(pdf_file_path)
