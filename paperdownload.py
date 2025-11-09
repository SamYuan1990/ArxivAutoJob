import tarfile
import os
import requests
import datetime
import pandas as pd
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm
import base64
import arxiv
from utils import update_csv

def ToBase64(file):
    with open(file, 'rb') as fileObj:
        data = fileObj.read()
    base64_data = base64.b64encode(data)
    return base64_data

def archive_dir(dir_name, output_filename, format="zip"):
    shutil.make_archive(output_filename, format, dir_name)
    return output_filename + ".zip"
    
def make_dir_if_not_exist(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def untar(fname, dirs):
    """
    解压tar.gz文件
    :param fname: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """
    try:
        t = tarfile.open(fname)
        t.extractall(path=dirs)
        return True
    except Exception as e:
        print(e)
        return False
    
def get_timestamp():
    ts = pd.to_datetime(str(datetime.datetime.now()))
    d = ts.strftime('%Y%m%d%H%M%S')
    return d

def get_paper_info_from_arxiv(arxiv_id):
    """
    使用arxiv库获取论文信息
    
    :param arxiv_id: 论文ID
    :return: 包含标题和提交日期的字典，或None
    """
    try:
        # 使用arxiv库搜索论文
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        if paper:
            return {
                'title': paper.title,
                'published': paper.published.strftime('%Y-%m-%d'),  # 首次发布日期
                'updated': paper.updated.strftime('%Y-%m-%d') if paper.updated else None
            }
        return None
    except Exception as e:
        print(f"通过arxiv库获取论文信息失败 {arxiv_id}: {e}")
        return None

def download_arxiv_papers_from_csv(csv_file_path, output_base="data"):
    """
    从CSV文件读取论文编码并下载LaTeX版本
    
    :param csv_file_path: CSV文件路径
    :param output_base: 输出基础目录
    """
    print("start download_arxiv_papers_from_csv")
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_file_path)
        print(f"成功读取CSV文件，共{len(df)}行数据")
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 确保输出目录存在
    make_dir_if_not_exist(output_base)
    
    # 记录需要更新的数据
    updates_needed = []
    
    # 遍历每一行数据
    for index, row in tqdm(df.iterrows(), total=len(df), desc="下载论文"):
        arxiv_id = str(row['arxiv_id']).strip()
        
        # 跳过空值或无效的arxiv_id
        if not arxiv_id or arxiv_id == 'nan':
            print(f"跳过第{index+1}行，无效的arxiv_id")
            continue
        
        # 创建论文专属目录
        paper_dir = os.path.join(output_base, arxiv_id.replace('/', '-'))
        make_dir_if_not_exist(paper_dir)
        
        # 检查是否已经下载过
        already_downloaded = os.path.exists(os.path.join(paper_dir, "source.tar.gz"))
        
        # 使用arxiv库获取论文信息（包括提交日期）
        paper_info = get_paper_info_from_arxiv(arxiv_id)
        
        if paper_info:
            submission_date = paper_info['published']  # 首次提交日期
            title = paper_info['title'].replace(" ", "-").replace("/", "-").replace("\\", "-")
            
            # 检查当前日期是否需要更新
            current_date = row.get('date')
            if pd.isna(current_date) or str(current_date) == 'nan' or not current_date:
                updates_needed.append((arxiv_id, submission_date))
                print(f"需要更新 {arxiv_id} 的日期为: {submission_date}")
            else:
                print(f"{arxiv_id} 已有日期: {current_date}")
        else:
            print(f"无法获取 {arxiv_id} 的论文信息")
            title = arxiv_id.replace('/', '-')
            submission_date = None
        
        # 如果已经下载过，跳过下载步骤
        if already_downloaded:
            print(f"论文 {arxiv_id} 已存在，跳过下载")
            # 即使已下载，也尝试更新日期
            if submission_date and (pd.isna(row.get('date')) or str(row.get('date')) == 'nan' or not row.get('date')):
                update_csv(csv_file_path, arxiv_id,"date", submission_date)
                update_csv(csv_file_path, arxiv_id, "downloaded", "True")
            continue
        
        try:
            print(f"正在下载论文: {arxiv_id} - {title}")
            
            # 下载源代码
            source_link = f"https://arxiv.org/e-print/{arxiv_id}"
            response = requests.get(source_link, timeout=30)
            
            if response.status_code == 200:
                # 保存tar.gz文件
                tar_path = os.path.join(paper_dir, "source.tar.gz")
                with open(tar_path, "wb") as f:
                    f.write(response.content)
                
                # 解压文件
                extract_dir = os.path.join(paper_dir, "content")
                make_dir_if_not_exist(extract_dir)
                
                if untar(tar_path, extract_dir):
                    print(f"成功下载并解压论文: {arxiv_id}")
                    
                    # 保存论文信息
                    info_file = os.path.join(paper_dir, "paper_info.txt")
                    with open(info_file, 'w', encoding='utf-8') as f:
                        f.write(f"arXiv ID: {arxiv_id}\n")
                        f.write(f"Title: {title}\n")
                        f.write(f"Download Time: {datetime.datetime.now()}\n")
                        if submission_date:
                            f.write(f"First Submission Date: {submission_date}\n")
                        if 'date' in row and pd.notna(row['date']):
                            f.write(f"Original Date in CSV: {row['date']}\n")
                        if 'position_index' in row and pd.notna(row['position_index']):
                            f.write(f"Position Index: {row['position_index']}\n")
                        if 'initiative_index' in row and pd.notna(row['initiative_index']):
                            f.write(f"Initiative Index: {row['initiative_index']}\n")
                    
                    # 更新CSV中的日期
                    if submission_date:
                        update_csv(csv_file_path, arxiv_id, "date", submission_date)
                        update_csv(csv_file_path, arxiv_id, "downloaded", "True")
                
                else:
                    print(f"解压论文 {arxiv_id} 失败")
                    
            else:
                print(f"下载论文 {arxiv_id} 失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"处理论文 {arxiv_id} 时出错: {e}")
            continue
    
    print("所有论文处理完成！")

def download_single_arxiv_paper(arxiv_id, output_base="data"):
    """
    下载单个arXiv论文
    
    :param arxiv_id: arXiv论文ID
    :param output_base: 输出基础目录
    """
    # 创建论文专属目录
    paper_dir = os.path.join(output_base, arxiv_id.replace('/', '-'))
    make_dir_if_not_exist(paper_dir)
    
    try:
        # 使用arxiv库获取论文信息
        paper_info = get_paper_info_from_arxiv(arxiv_id)
        
        if paper_info:
            title = paper_info['title'].replace(" ", "-").replace("/", "-").replace("\\", "-")
            submission_date = paper_info['published']
        else:
            title = arxiv_id.replace('/', '-')
            submission_date = None
        
        print(f"正在下载论文: {arxiv_id} - {title}")
        
        # 下载源代码
        source_link = f"https://arxiv.org/e-print/{arxiv_id}"
        response = requests.get(source_link, timeout=30)
        
        if response.status_code == 200:
            # 保存tar.gz文件
            tar_path = os.path.join(paper_dir, "source.tar.gz")
            with open(tar_path, "wb") as f:
                f.write(response.content)
            
            # 解压文件
            extract_dir = os.path.join(paper_dir, "content")
            make_dir_if_not_exist(extract_dir)
            
            if untar(tar_path, extract_dir):
                print(f"成功下载并解压论文: {arxiv_id}")
                
                # 保存论文信息
                info_file = os.path.join(paper_dir, "paper_info.txt")
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"arXiv ID: {arxiv_id}\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Download Time: {datetime.datetime.now()}\n")
                    if submission_date:
                        f.write(f"First Submission Date: {submission_date}\n")
                
                return True, submission_date
            else:
                print(f"解压论文 {arxiv_id} 失败")
                return False, None
        else:
            print(f"下载论文 {arxiv_id} 失败，状态码: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"处理论文 {arxiv_id} 时出错: {e}")
        return False, None
