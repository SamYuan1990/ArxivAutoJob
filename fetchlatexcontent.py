import re
from pathlib import Path

def extract_latex_fields(paper_path: str) -> dict:
    """简化版的提取函数"""
    paper_dir = Path(paper_path)
    
    # 查找tex文件
    tex_files = list(paper_dir.glob("*.tex"))
    if not tex_files:
        return {}
    
    # 读取所有内容
    content = ""
    for tex_file in tex_files:
        try:
            content += tex_file.read_text(encoding='utf-8', errors='ignore') + "\n"
        except:
            continue
    
    def clean_text(text):
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\[a-zA-Z]+\*?\s*', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # 提取各个字段
    title = ""
    abstract = ""
    introduction = ""
    conclusions = ""
    
    # 提取标题
    title_match = re.search(r'\\title\{(.*?)\}', content, re.DOTALL)
    if title_match:
        title = clean_text(title_match.group(1))
    
    # 提取摘要
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    if abstract_match:
        abstract = clean_text(abstract_match.group(1))
    
    # 提取引言
    intro_match = re.search(r'\\section\*?\{(.*?[Ii]ntroduction.*?)\}(.*?)(?=\\section|$)', content, re.DOTALL)
    if intro_match:
        introduction = clean_text(intro_match.group(2))
    
    # 提取结论
    concl_match = re.search(r'\\section\*?\{(.*?[Cc]onclusion.*?)\}(.*?)(?=\\section|$)', content, re.DOTALL)
    if concl_match:
        conclusions = clean_text(concl_match.group(2))
    
    return {
        "title": title,
        "abstract": abstract,
        "introduction": introduction,
        "conclusions": conclusions
    }

