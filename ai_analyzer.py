"""AI analysis functionality for arXiv papers."""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from openai import OpenAI, AsyncOpenAI
import os

logger = logging.getLogger(__name__)

# Load the default prompt from an external file
try:
    with open(Path(__file__).parent / "prompt.txt", "r", encoding="utf-8") as f:
        DEFAULT_PROMPT = f.read()
except FileNotFoundError:
    logger.error("prompt.txt not found. Please create it.")
    DEFAULT_PROMPT = "Please summarize this paper." # Fallback prompt


async def analyze_paper_with_ai_async(
    paper_content: str,
    paper_id: str,
    prompt: str = DEFAULT_PROMPT
) -> Optional[Dict[str, Any]]:
    """
    Analyze a paper using AI and return structured results (asynchronous version).
    Reads configuration from environment variables.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
        model = os.getenv("OPENAI_MODEL", "deepseek-chat")

        if not api_key:
            raise ValueError("API key is required. Please set OPENAI_API_KEY.")
            
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        # Create task
        task = f"{prompt}\n\n论文内容:\n\n{paper_content}"
        
        # Request AI analysis
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个乐于助人的助手，专门分析学术论文。所有内容都用中文输出。"},
                {"role": "user", "content": task},
            ],
            stream=False
        )
        
        # Parse response
        content = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            # Clean up potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            analysis_result = json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic structure
            analysis_result = {
                "title": paper_id,
                "summary": content,
                "error": "Failed to parse JSON response from AI."
            }
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"AI analysis failed for {paper_id}: {str(e)}")
        return None


from paper_downloader import get_paper_path

def save_analysis_result(
    paper_id: str,
    paper_title: str,
    analysis_result: Dict[str, Any],
    output_dir: str = "./download"
) -> bool:
    """
    Save analysis result to JSON file.
    
    Args:
        paper_id: Paper ID
        analysis_result: Analysis result dictionary
        output_dir: Directory to save the result
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use get_paper_path to construct the correct filename
        output_file = get_paper_path(paper_id, paper_title, "_analysis.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Analysis result saved for {paper_id} to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save analysis result for {paper_id}: {str(e)}")
        return False
