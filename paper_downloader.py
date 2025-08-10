"Download and conversion functionality for arXiv papers."

import arxiv
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import pymupdf4llm
import re

logger = logging.getLogger(__name__)

# Global dictionary to track download status (for potential future use, not used by pipeline)
download_statuses: Dict[str, Any] = {}

def sanitize_filename(filename: str) -> str:
    """Remove potentially unsafe characters from a filename."""
    # Replace slashes with underscores
    filename = filename.replace('/', '_')
    # Remove other invalid filesystem characters
    sanitized = re.sub(r'[\:*?"<>|]', '', filename).strip()
    # Truncate to a reasonable length
    return sanitized[:180] 

def get_paper_path(paper_id: str, paper_title: str, suffix: str) -> Path:
    """Get the absolute file path for a paper with the new filename format."""
    safe_paper_id = sanitize_filename(paper_id)
    safe_title = sanitize_filename(paper_title)
    
    filename = f"{safe_paper_id} - {safe_title}{suffix}"
    
    storage_path = Path('./download')
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path / filename

def download_paper_sync(paper_id: str, paper_title: str) -> bool:
    """Downloads a single paper PDF synchronously."""
    try:
        pdf_path = get_paper_path(paper_id, paper_title, ".pdf")
        if pdf_path.exists():
            logger.info(f"PDF for {paper_id} already exists. Skipping download.")
            return True

        client = arxiv.Client(page_size=1, delay_seconds=0.1, num_retries=3)
        paper = next(client.results(arxiv.Search(id_list=[paper_id])))
        paper.download_pdf(dirpath=pdf_path.parent, filename=pdf_path.name)
        logger.info(f"Download completed for {paper_id}")
        return True
    except StopIteration:
        logger.error(f"Paper {paper_id} not found on arXiv")
        return False
    except Exception as e:
        logger.error(f"Download failed for {paper_id}: {str(e)}")
        return False

import subprocess
import sys

def convert_paper_sync(paper_id: str, paper_title: str) -> bool:
    """Converts a PDF to Markdown by running a separate, safe process."""
    pdf_path = get_paper_path(paper_id, paper_title, ".pdf")
    md_path = get_paper_path(paper_id, paper_title, ".md")

    if not pdf_path.exists():
        logger.error(f"Cannot convert {paper_id}: PDF file not found at {pdf_path}")
        return False
    
    if md_path.exists():
        logger.info(f"Markdown for {paper_id} already exists. Skipping conversion.")
        return True

    try:
        # Find the python executable that is running the current script
        python_executable = sys.executable
        converter_script_path = Path(__file__).parent / "safe_converter.py"

        # Run the conversion in a separate process to isolate crashes
        result = subprocess.run(
            [python_executable, str(converter_script_path), str(pdf_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=180  # Add a 3-minute timeout for safety
        )

        # Check if the subprocess crashed or reported an error
        if result.returncode != 0:
            logger.error(f"Safe converter subprocess failed for {paper_id} with exit code {result.returncode}.")
            logger.error(f"Stderr: {result.stderr}")
            return False

        # Write the output from the successful subprocess to the markdown file
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        
        logger.info(f"Conversion completed for {paper_id} via safe subprocess.")
        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Conversion process for {paper_id} timed out after 180 seconds.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while managing the conversion subprocess for {paper_id}: {e}")
        return False
