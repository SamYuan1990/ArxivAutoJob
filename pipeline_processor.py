"""Pipeline processor for ArxivAutoJob system with a streaming architecture."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from arxiv_search import search_papers
from paper_downloader import download_paper_sync, convert_paper_sync, get_paper_path
from ai_analyzer import analyze_paper_with_ai_async, save_analysis_result
from report_generator import ReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineProcessor:
    """Processes papers using a streaming pipeline architecture."""
    
    def __init__(
        self,
        download_workers: int = 3,
        conversion_workers: int = 3,
        analysis_workers: int = 3
    ):
        self.download_workers = download_workers
        self.conversion_workers = conversion_workers
        self.analysis_workers = analysis_workers
        self.report_generator = ReportGenerator()
        self.conversion_queue = asyncio.Queue()
        self.analysis_queue = asyncio.Queue()

    async def _downloader(self, papers: List[Dict[str, Any]], executor: ThreadPoolExecutor):
        """Downloads papers and puts them in the conversion queue."""

        async def download_task(paper):
            """Wrapper coroutine for a single download task that returns success and the paper."""
            loop = asyncio.get_running_loop()
            success = await loop.run_in_executor(
                executor, download_paper_sync, paper['id'], paper['title']
            )
            return success, paper

        tasks = [download_task(paper) for paper in papers]

        for future in asyncio.as_completed(tasks):
            try:
                success, paper = await future
                if success:
                    logger.info(f"Downloaded {paper['id']}, queueing for conversion.")
                    await self.conversion_queue.put(paper)
                else:
                    logger.warning(f"Download task for {paper['id']} failed, not queueing for conversion.")
            except Exception as e:
                logger.error(f"A download wrapper task failed unexpectedly: {e}")

        # Signal that downloading is done
        logger.info("All download tasks have completed. Signaling converters to close once queue is empty.")
        for _ in range(self.conversion_workers):
            await self.conversion_queue.put(None)

    async def _converter(self, executor: ThreadPoolExecutor):
        """Takes papers from conversion queue, converts them, and puts in analysis queue."""
        loop = asyncio.get_running_loop()
        while True:
            paper = await self.conversion_queue.get()
            if paper is None:
                # This converter is done
                break

            try:
                success = await loop.run_in_executor(executor, convert_paper_sync, paper['id'], paper['title'])
                if success:
                    logger.info(f"Converted {paper['id']}, queueing for analysis.")
                    await self.analysis_queue.put(paper)
            except Exception as e:
                logger.error(f"Error converting {paper['id']}: {e}")
            finally:
                self.conversion_queue.task_done()

    async def _analyzer(self):
        """Takes papers from analysis queue and analyzes them."""
        while True:
            paper = await self.analysis_queue.get()
            if paper is None:
                # This analyzer is done
                break

            try:
                await self._analyze_single_paper(paper)
            except Exception as e:
                logger.error(f"Error analyzing {paper['id']}: {e}")
            finally:
                self.analysis_queue.task_done()

    async def _analyze_single_paper(self, paper: Dict[str, Any]) -> bool:
        """Analyzes a single paper and saves the result."""
        paper_id = paper.get('id')
        paper_title = paper.get('title', 'Untitled')
        logger.info(f"Analyzing paper {paper_id} with AI")
        
        paper_md_file = get_paper_path(paper_id, paper_title, ".md")
        if not paper_md_file.exists():
            logger.error(f"Paper file not found for {paper_id}")
            return False
            
        with open(paper_md_file, 'r', encoding='utf-8') as f:
            paper_content = f.read()
            
        analysis_result = await analyze_paper_with_ai_async(
            paper_content=paper_content,
            paper_id=paper_id
        )
        
        if not analysis_result:
            logger.error(f"AI analysis failed for {paper_id}")
            return False

        analysis_result['published'] = paper.get('published')
        
        if not save_analysis_result(paper_id, paper_title, analysis_result):
            logger.error(f"Failed to save analysis result for {paper_id}")
            return False
            
        logger.info(f"Successfully analyzed paper {paper_id}")
        return True

    async def process_papers(
        self,
        categories: List[str] = None,
        max_results: int = 50,
        days_back: int = 7
    ) -> None:
        """Processes papers through the entire streaming pipeline."""
        logger.info("Starting ArxivAutoJob streaming pipeline")
        
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"]
        
        now = datetime.now()
        date_from = now - timedelta(days=days_back)
        
        logger.info(f"Searching for papers from {date_from.date()} to {now.date()} in {categories}")
        papers = search_papers(
            search_query="",
            categories=categories,
            date_from=date_from,
            date_to=now,
            max_results=max_results
        )
        
        if not papers:
            logger.info("No new papers found. Exiting.")
            return
            
        logger.info(f"Found {len(papers)} papers to process.")

        with ThreadPoolExecutor(max_workers=self.download_workers) as dl_executor:
            with ThreadPoolExecutor(max_workers=self.conversion_workers) as conv_executor:
                downloader_task = asyncio.create_task(self._downloader(papers, dl_executor))
                
                converter_tasks = [
                    asyncio.create_task(self._converter(conv_executor))
                    for _ in range(self.conversion_workers)
                ]
                
                analyzer_tasks = [
                    asyncio.create_task(self._analyzer())
                    for _ in range(self.analysis_workers)
                ]

                # Wait for the downloader to finish. It will signal the converters.
                await downloader_task
                logger.info("Downloader has finished.")

                # Wait for all converters to finish their work and exit.
                await asyncio.gather(*converter_tasks)
                logger.info("All converters have finished.")

                # Now that all converters are done, we know no more items will be added
                # to the analysis queue. We can now signal the analyzers to stop.
                for _ in range(self.analysis_workers):
                    await self.analysis_queue.put(None)
                
                # Wait for all analyzers to finish their work and exit.
                await asyncio.gather(*analyzer_tasks)
                logger.info("All analyzers have finished.")

        logger.info("Regenerating complete RSS feed and Markdown summary...")
        self.report_generator.regenerate_complete_feed()
        self.report_generator.generate_markdown_summary()
        
        logger.info("ArxivAutoJob streaming pipeline processing completed successfully")
