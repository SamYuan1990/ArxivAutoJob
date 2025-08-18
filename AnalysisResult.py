from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class CommunicationMethod(BaseModel):
    category: str
    fact_check_keywords: List[str]

class AnalysisResult(BaseModel):
    Subject: List[str]
    Predicate:  List[str]
    Object:  List[str]
    Attributive:  List[str]
    Adverbial:  List[str]
    Complement:  List[str]
    Others:  List[str]
    Emotional_intensity: int
    CommunicationMethods: List[CommunicationMethod]

class Sentence(BaseModel):
    origin_text: str
    need_Analysis: Optional[bool] = None
    AnalysisResult: Optional[AnalysisResult] = None
    Emotional_intensity: Optional[int] = None
    SPO_Score: Optional[float] = None
    summary: Optional[str] = None
    CommunicationMethods: Optional[List[CommunicationMethod]] = None


def generate_markdown_output(sentence: Sentence) -> str:
    # 处理红色标记的成分
    marked_text = sentence.origin_text
    analysis = sentence.AnalysisResult
    # 标记Subject
    for subj in analysis.Subject:
        marked_text = marked_text.replace(subj, f'<span style="color: #4589ff;">{subj}</span>')
    
    # 标记Predicate
    for pred in analysis.Predicate:
        marked_text = marked_text.replace(pred, f'<span style="color: #4589ff;">{pred}</span>')
    
    # 标记Object
    for obj in analysis.Object:
        marked_text = marked_text.replace(obj, f'<span style="color: #4589ff;">{obj}</span>')
    
    # 构建传播学方法部分
    comm_methods = []
    for method in sentence.CommunicationMethods:
        keywords = ", ".join(method.fact_check_keywords)
        comm_methods.append(f"- {method.category}\n> - 事实核实关键字: [{keywords}]")
    
    # 组合最终Markdown
    markdown = (
        f"<details>\n"
        f"  <summary>{marked_text}</summary>\n\n"
        f"  SPO: {sentence.SPO_Score}, 情感: {sentence.Emotional_intensity} \n"
        f"  **传播学方法**:\n"
        f"  > " + "\n  > ".join(comm_methods) + "\n"
        f"</details>"
    )
    
    return markdown

def write_results_to_markdown(sentence: Sentence, output_file: str = "test123.md"):
    """
    将摘要结果和分析结果写入Markdown文件
    
    :param summary_result: 摘要文本字符串
    :param analysis_results: 包含Sentence对象的列表
    :param output_file: 输出文件名，默认为"test123.md"
    """
    with open(output_file, 'a', encoding='utf-8') as f:
        if not sentence.need_Analysis:
             f.write(sentence.origin_text)
             f.write("\n")
             return
        else:
            # 写入摘要部分
            f.write("# 分析摘要\n")
            f.write(sentence.summary)
            f.write("\n\n")
            
            # 写入每个分析结果
            f.write("# 详细分析\n")
            markdown_output = generate_markdown_output(sentence)
                #f.write(f"## 句子 {i}\n")
            f.write(markdown_output)
            f.write("\n\n")
