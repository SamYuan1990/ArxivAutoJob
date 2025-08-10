"""
Main entry point for the ArxivAutoJob system.

This script initializes and runs the main pipeline processor, which is the
recommended way to run this application. It can be configured via command-line
arguments.
"""

import asyncio
import logging
import argparse
from pipeline_processor import PipelineProcessor

def setup_logging(level=logging.INFO):
    """Set up logging configuration to show only necessary information."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    # Reduce verbosity for noisy libraries
    logging.getLogger('arxiv').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)

async def main(args):
    """
    Initializes and runs the ArxivAutoJob pipeline based on provided arguments.
    """
    logging.info("Starting ArxivAutoJob using the main pipeline processor...")
    
    # Initialize the pipeline processor with desired concurrency settings.
    processor = PipelineProcessor(
        download_workers=5,
        conversion_workers=5,
        analysis_workers=3
    )
    
    # Process papers using parameters from command-line arguments.
    await processor.process_papers(
        categories=args.categories,
        max_results=args.max_results,
        days_back=args.days_back
    )
    
    logging.info("ArxivAutoJob processing finished.")

if __name__ == "__main__":
    # Setup logging first
    setup_logging()

    parser = argparse.ArgumentParser(
        description="ArxivAutoJob: An automated pipeline to fetch, analyze, and report on arXiv papers."
    )
    parser.add_argument(
        '--categories', 
        nargs='+', 
        default=['cs.AI', 'cs.LG'],
        help='List of arXiv categories to search (e.g., cs.AI cs.LG cs.CV cs.CL).'
    )
    parser.add_argument(
        '--max-results', 
        type=int, 
        default=25,
        help='Maximum number of papers to process.'
    )
    parser.add_argument(
        '--days-back', 
        type=int, 
        default=7,
        help='Number of days back to search for new papers.'
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
