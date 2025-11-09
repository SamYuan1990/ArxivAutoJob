import os
from paperdownload import download_arxiv_papers_from_csv

def main():
    csv_file_path = "data/data.csv"
    
    # 检查CSV文件是否存在
    if os.path.exists(csv_file_path):
        print("开始从CSV文件批量下载论文...")
        download_arxiv_papers_from_csv(csv_file_path)
        print("批量下载完成！")
    else:
        print(f"CSV文件不存在: {csv_file_path}")
        print("请确保data/data.csv文件存在")

main()