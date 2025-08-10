from typing import List
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
    AnalysisResult: AnalysisResult
    Emotional_intensity: int
    SPO_Score: float
    CommunicationMethods: List[CommunicationMethod]


def generate_markdown_output(sentence: Sentence) -> str:
    # 处理红色标记的成分
    marked_text = sentence.origin_text
    analysis = sentence.AnalysisResult
    
    # 标记Subject
    for subj in analysis.Subject:
        marked_text = marked_text.replace(subj, f'<font color="red">{subj}</font>')
    
    # 标记Predicate
    for pred in analysis.Predicate:
        marked_text = marked_text.replace(pred, f'<font color="red">{pred}</font>')
    
    # 标记Object
    for obj in analysis.Object:
        marked_text = marked_text.replace(obj, f'<font color="red">{obj}</font>')
    
    # 构建传播学方法部分
    comm_methods = []
    for method in sentence.CommunicationMethods:
        keywords = ", ".join(method.fact_check_keywords)
        comm_methods.append(f"- {method.category}\n> - 事实核实关键字: [{keywords}]")
    
    # 组合最终Markdown
    markdown = (
        f"{marked_text}\n"
        f"<details>\n"
        f"  <summary>SPO: {sentence.SPO_Score}, 情感: {sentence.Emotional_intensity}</summary>\n\n"
        f"  **传播学方法**:\n"
        f"  > " + "\n  > ".join(comm_methods) + "\n"
        f"</details>"
    )
    
    return markdown

def write_results_to_markdown(summary_result: str, analysis_results: list, output_file: str = "test123.md"):
    """
    将摘要结果和分析结果写入Markdown文件
    
    :param summary_result: 摘要文本字符串
    :param analysis_results: 包含Sentence对象的列表
    :param output_file: 输出文件名，默认为"test123.md"
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入摘要部分
        f.write("# 分析摘要\n")
        f.write(summary_result)
        f.write("\n\n")
        
        # 写入每个分析结果
        f.write("# 详细分析\n")
        for i, result in enumerate(analysis_results, 1):
            markdown_output = generate_markdown_output(result)
            #f.write(f"## 句子 {i}\n")
            f.write(markdown_output)
            f.write("\n\n")

#test_sentence = Sentence(
#    origin_text="苹果公司发布了新款iPhone",
#    AnalysisResult=AnalysisResult(
#        Subject=["苹果公司"],
#        Predicate=["发布"],
#        Object=["新款iPhone"],
#        Attributive=["新款"],
#        Adverbial=[],
#        Complement=[],
#        Others=[],
#        Emotional_intensity=3,
#        CommunicationMethods=[],
#    ),
#    Emotional_intensity=3,
#    SPO_Score=5.5,
#    CommunicationMethods=[
#        CommunicationMethod(
#            category="科技产品发布",
#            fact_check_keywords=["iPhone", "发布会"]
#        ),
#        CommunicationMethod(
#            category="品牌营销",
#            fact_check_keywords=["苹果", "市场营销"]
#        )
#    ]
#)

# 生成并打印Markdown
#print(generate_markdown_output(test_sentence))