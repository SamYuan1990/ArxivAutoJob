import re

def split_markdown_by_headings(file_path):
    """
    读取Markdown文件并按一级(#)或二级(##)标题分段返回内容
    
    :param file_path: Markdown文件路径
    :return: 分段后的内容列表
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用正则表达式分割内容，匹配一级或二级标题
    # 正则解释：^匹配行开头，\s*可能有空白，#{1,2}匹配1-2个#，后面跟着至少一个空格，然后是标题文字
    sections = re.split(r'(^#+\s+.+$)', content, flags=re.MULTILINE)
    
    # 过滤掉空字符串
    sections = [section.strip() for section in sections if section.strip()]
    
    # 合并标题和内容
    result = []
    for i in range(0, len(sections), 2):
        if i+1 < len(sections):
            # 如果有内容，将标题和内容合并
            result.append(f"{sections[i]}\n{sections[i+1]}")
        else:
            # 如果最后只剩下标题
            result.append(sections[i])
    
    return result

# 使用示例
#file_path = "LLM.md"  # 替换为你的Markdown文件路径
#sections = split_markdown_by_headings(file_path)

#for i, section in enumerate(sections, 1):
#    print(f"=== 第{i}段 ===")
#    print(section)
#    print("\n")