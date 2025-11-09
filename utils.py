import pandas as pd
import re

def update_csv(csv_file_path, arxiv_id, column, data):
    """
    更新CSV文件中指定arxiv_id的指定列数据
    
    :param csv_file_path: CSV文件路径
    :param arxiv_id: 论文ID
    :param column: 要更新的列名
    :param data: 新的数据（单个值或与匹配行数相同的可迭代对象）
    """
    try:
        df = pd.read_csv(csv_file_path)
        
        # 调试信息
        print(f"CSV中的arxiv_id列表: {df['arxiv_id'].tolist()}")
        print(f"要查找的arxiv_id: '{arxiv_id}'")
        print(f"数据类型 - CSV中的id: {type(df['arxiv_id'].iloc[0])}, 查找的id: {type(arxiv_id)}")
        print(f"要更新的列: {column}")
        print(f"新数据的类型: {type(data)}")
        if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            print(f"数据长度: {len(list(data))}")
        
        # 清理arxiv_id
        clean_arxiv_id = str(arxiv_id).strip()
        
        # 多种匹配方式
        df['arxiv_id_clean'] = df['arxiv_id'].astype(str).str.strip()
        
        # 方式1：精确匹配
        mask_clean = df['arxiv_id_clean'] == clean_arxiv_id
        
        # 方式2：包含匹配
        mask_contains = df['arxiv_id_clean'].str.contains(re.escape(clean_arxiv_id), na=False, regex=True)
        
        # 方式3：使用正则表达式匹配（处理版本号等）
        pattern = re.escape(clean_arxiv_id)
        mask_regex = df['arxiv_id_clean'].str.contains(pattern, na=False, regex=True)
        
        # 选择第一个有效的匹配掩码
        final_mask = None
        for mask, method_name in [(mask_clean, "精确匹配"), 
                                 (mask_contains, "包含匹配"), 
                                 (mask_regex, "正则匹配")]:
            match_count = mask.sum()
            if match_count > 0:
                print(f"使用 {method_name} 找到 {match_count} 个匹配项")
                final_mask = mask
                break
        
        if final_mask is not None and final_mask.any():
            match_count = final_mask.sum()
            
            # 处理数据赋值 - 确保长度匹配
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                # 如果data是可迭代对象（但不是字符串）
                data_list = list(data)
                if len(data_list) == match_count:
                    # 长度匹配，直接赋值
                    df.loc[final_mask, column] = data_list
                    print(f"✓ 数据长度与匹配行数一致，直接赋值")
                elif len(data_list) == 1:
                    # 只有一个元素，广播到所有匹配行
                    df.loc[final_mask, column] = data_list[0]
                    print(f"✓ 数据只有1个元素，广播到所有{match_count}个匹配行")
                else:
                    # 长度不匹配，将所有元素用下划线拼接
                    concatenated_data = "_".join(str(item) for item in data_list)
                    df.loc[final_mask, column] = concatenated_data
                    print(f"⚠ 数据长度({len(data_list)})与匹配行数({match_count})不匹配，已将所有元素拼接: {concatenated_data}")
            else:
                # 单个值，广播到所有匹配行
                df.loc[final_mask, column] = data
                print(f"✓ 单个值数据，广播到所有{match_count}个匹配行")
            
            # 保存CSV文件
            df = df.drop('arxiv_id_clean', axis=1)  # 删除临时列
            df.to_csv(csv_file_path, index=False)
            print(f"✓ 已更新CSV中 {arxiv_id} 的 {column} 列")
            print(f"✓ 成功更新了 {match_count} 行数据")
            return True
        else:
            print(f"✗ 在CSV中未找到 {arxiv_id}")
            print(f"可用的ID: {df['arxiv_id_clean'].tolist()}")
            return False
            
    except Exception as e:
        print(f"更新CSV文件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False