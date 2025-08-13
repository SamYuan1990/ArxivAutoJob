from AnalysisAgent import AnalysisAgent
from SummaryAgent import SummaryAgent
from spo_score import filter_high_spo_sentences
from filereader import split_markdown_by_headings
from init_configs import init_configs
from AnalysisResult import write_results_to_markdown
from deepSeekmodel import DeepSeekModel

import concurrent.futures
import time
import re
import os

def process_paragraph(model,config,paragraph):
    model = DeepSeekModel(
        api_key=os.environ["api_key"],
        base_url="https://api.deepseek.com",
        model_id="deepseek-chat",
    )
    analysisAgent = AnalysisAgent(
        config=config,
        model=model
    )
    messages = re.split(r'[。！？\n]\s*', paragraph.strip())
    messages = [s.strip() for s in messages if s.strip()]
    analysis_results = analysisAgent.process_messages(messages)
    filtered_sentences = filter_high_spo_sentences(analysis_results)
    summary_agent = SummaryAgent(
        config=config,
        model=model
    )
    summary_result = summary_agent.summary(filtered_sentences)
    return {
        "summary_result": str(summary_result),
        "analysis_result": analysis_results,
    }

def process_preserve_order(model, config, input_text):
    paragraphs = re.split(r'(^#+\s+.+$)', input_text, flags=re.MULTILINE)
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    merged_paragraphs = []
    i = 0
    n = len(paragraphs)

    while i < n:
        current = paragraphs[i]
        # If current paragraph is too short and not the last one
        if len(current) < 100 and i < n - 1:
            # Merge with next paragraph
            merged = current + " " + paragraphs[i+1]
            merged_paragraphs.append(merged)
            i += 2  # Skip next paragraph since we merged it
        else:
            merged_paragraphs.append(current)
            i += 1
    paragraphs = merged_paragraphs
    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交任务并保留原始索引
        futures = {
            executor.submit(process_paragraph, model, config, paragraph): idx
            for idx, paragraph in enumerate(paragraphs)
        }
        
        # 初始化结果列表（按原始顺序）
        results = [None] * len(paragraphs)
        
        # 按完成顺序获取结果，但按原始索引存储
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
    
    return results

if __name__ == "__main__":
    # 示例输入（含多个自然段）
    model, config = init_configs()
    file_name = "2507.21046v3"
    with open(file_name+".md", 'r', encoding='utf-8') as file:
        input_text = file.read()
    
    start_time = time.time()
    processed_data = process_preserve_order(model, config, input_text.strip())
    elapsed_time = time.time() - start_time

    print("处理结果（保持自然段顺序）:")
    for data in processed_data:
        #print(f"段落: {data['sentence']}")
        #print(f"→ 字符数: {data['length']}, 单词数: {data['word_count']}\n")
        write_results_to_markdown(data['summary_result'],
                                  data['analysis_result'],
                                  file_name+"_result.md"
                                  )
    
    print(f"总耗时: {elapsed_time:.2f}秒（并发执行）")