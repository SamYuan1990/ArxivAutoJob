from AnalysisResult import Sentence
from deepseek_tokenizer import tokenizer

import logging
import re

def TextToParagraphs(input_text):
    pattern = r'(^#+\s+.+$|^\*\*.+\*\*|^!\[.*\]\(.+\)$)'
    paragraphs = re.split(pattern, input_text, flags=re.MULTILINE)
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    merged_paragraphs = []
    for i, current in enumerate(paragraphs):
        if tokenizer(current) < 50:
            logging.info("Skip analysis within 50 words")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=False,
                )
            )            
            continue

        if current.startswith('![') and current.endswith(')'):
            logging.info("picture don't need analysis with text only LLM")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=False,
                )
            )
            continue

        ref_pattern = r'^#{1,6}\s*\**References?\b'
        match = re.search(ref_pattern, current, flags=re.IGNORECASE)
        if match:
            logging.info("reference don't need analysis with text only LLM")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=False,
                )
            )
            break

        contents_pattern = r'(?:\. ){6,}\.?'  # 匹配7个或更多的连续点
        match = re.search(contents_pattern, current)
        if match:
            logging.info("Content need analysis with text only LLM")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=False,
                )
            )
            continue

        pic_pattern = r'^(?:Figure|Table)\b[\s:]*\d+[\s:]*.*'   # 匹配 "Figure 1:" 或 "Table 2 -" 等格式
        match = re.search(pic_pattern, current, flags=re.IGNORECASE)
        if match:
            logging.info("picture or table description need analysis with text only LLM")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=True,
                )
            )
            continue

        logging.info("Defualt analysis")
        merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=True,
                )
            )

    return merged_paragraphs
