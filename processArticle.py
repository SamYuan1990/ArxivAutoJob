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

        pic_pattern = r'^Figure\b[\s:]*\d+[\s:]*.*'  # 匹配 "Figure 1:" 或 "FIGURE 2 -" 等格式
        match = re.search(pic_pattern, current, flags=re.IGNORECASE)
        if match:
            logging.info("picture description need analysis with text only LLM")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=True,
                )
            )
            continue

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

        if tokenizer(current) < 50:
            logging.info("Skip analysis within 50 words")
            merged_paragraphs.append(
                Sentence(
                    origin_text=current,
                    need_Analysis=False,
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

#def print_first_10_words(strings_array):
#    for i, sentences in enumerate(strings_array, 1):
        # 分割字符串为单词列表
#        if sentences.need_Analysis:
#            words = sentences.origin_text.split()
            # 取前10个单词（如果不足10个则取全部）
#            first_10 = words[:10]
            # 将单词列表重新组合成字符串
#            result = ' '.join(first_10) + '\t' + str(len(words)) 
            # 打印结果（带序号）
#            print(f"{i}. {result}")


#file_name = "LLM"
#file_name="2507.21046v3"
#with open(file_name+".md", 'r', encoding='utf-8') as file:
#        input_text = file.read()

#print_first_10_words(TextToParagraphs(input_text))
