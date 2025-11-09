import pandas as pd

def update_csv(csv_file_path, arxiv_id, column, data):
    """
    更新CSV文件中指定arxiv_id的日期
    
    :param csv_file_path: CSV文件路径
    :param arxiv_id: 论文ID
    :param column: column
    :param data: new data
    """
    try:
        df = pd.read_csv(csv_file_path)
        
        # 调试信息：打印所有arxiv_id
        print(f"CSV中的arxiv_id列表: {df['arxiv_id'].tolist()}")
        print(f"要查找的arxiv_id: '{arxiv_id}'")
        print(f"数据类型 - CSV中的id: {type(df['arxiv_id'].iloc[0])}, 查找的id: {type(arxiv_id)}")
        
        # 清理arxiv_id：去除空格和特殊字符
        clean_arxiv_id = str(arxiv_id).strip()
        
        # 多种匹配方式
        # 方式1：精确匹配（清理空格）
        mask_clean = df['arxiv_id'].astype(str).str.strip() == clean_arxiv_id
        
        # 方式2：包含匹配
        mask_contains = df['arxiv_id'].astype(str).str.contains(clean_arxiv_id, na=False)
        
        # 方式3：使用正则表达式匹配（处理可能的版本号）
        import re
        mask_regex = df['arxiv_id'].astype(str).apply(
            lambda x: bool(re.search(re.escape(clean_arxiv_id), str(x))) if pd.notna(x) else False
        )
        
        # 使用第一种找到的匹配
        if mask_clean.any():
            df.loc[mask_clean, column] = data
            df.to_csv(csv_file_path, index=False)
            print(f"✓ 已更新CSV中 {arxiv_id} 的 {column} 为: {data}")
            return True
        elif mask_contains.any():
            df.loc[mask_contains, column] = data
            df.to_csv(csv_file_path, index=False)
            print(f"✓ 已更新CSV中 {arxiv_id} 的 {column} 为: {data}")
            return True
        elif mask_regex.any():
            df.loc[mask_regex, column] = data
            df.to_csv(csv_file_path, index=False)
            print(f"✓ 已更新CSV中 {arxiv_id} 的 {column} 为: {data}")
            return True
        else:
            print(f"✗ 在CSV中未找到 {arxiv_id}")
            print(f"可用的ID: {df['arxiv_id'].tolist()}")
            return False
            
    except Exception as e:
        print(f"更新CSV文件失败: {e}")
        return False