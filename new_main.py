from clientInfo import clientInfo
from metric import print_metrics
from AnalysisAgent import AnalysisAgent
from AnalysisResult import write_results_to_markdown
from processArticle import TextToParagraphs

import os
import re
import concurrent.futures

def process_paragraph(clientInfo, paragraph):
    print(paragraph)
    if paragraph.need_Analysis:
        AnalysisAgentInstance_1 = AnalysisAgent(clientInfo)
        AnalysisAgentInstance_1.set_msg(paragraph)
        analysis_results = AnalysisAgentInstance_1.analysis()
        summary_result=AnalysisAgentInstance_1.summary()
        return {
                "summary_result": str(summary_result),
                "analysis_result": analysis_results,
            }
    else:
        return {
                "summary_result": "",
                "analysis_result": [paragraph],
            }

def process_preserve_order(clientInfo, input_text):
    paragraphs = TextToParagraphs(input_text)
    # 使用线程池并发处理
    print(len(paragraphs))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 提交任务并保留原始索引
        futures = {
            executor.submit(process_paragraph, clientInfo, paragraph): idx
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
    LLM_Client = clientInfo(
        api_key=os.getenv("api_key"),
        base_url=os.getenv("base_url", "https://api.deepseek.com"),
        model=os.getenv("model", "deepseek-chat"),
        dryRun=os.getenv("dryRun", False),
    )
    LLM_Client.show_config()

    #file_name = "2507.21046v3"
    file_name = "laomutest"
    with open(file_name+".md", 'r', encoding='utf-8') as file:
        input_text = file.read()
    processed_data = process_preserve_order(LLM_Client, input_text.strip())
    print("start file output writing")
    for data in processed_data:
        write_results_to_markdown(data['summary_result'],
                                  data['analysis_result'],
                                  file_name+"_result.md"
                                  )
    print_metrics()
