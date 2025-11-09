import json
import asyncio
from arxiv_mcp_server.tools import handle_search
from datetime import datetime, timedelta
from openai import OpenAI
from download import handle_download,get_paper_path
import os

# 获取环境变量（字符串类型）
prompt = """
*用2-3句话总结论文
*这篇论文的主要贡献是什么？
*本文解决的主要问题是什么？
*本文使用的主要方法是什么？
*这篇论文的主要结果是什么？
*本文的主要结论是什么？
*本文的主要结论可能对生产生活产生哪些影响？
*本文的主要结论如何对生产生活产生影响？
*如果文中存在github链接，帮忙按顺序整理
"""


async def main():
    now = datetime.now()
    # to do update to 24
    past_24h = now - timedelta(hours=168)
    api_key = os.getenv("API_KEY")  # 返回None如果不存在
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    # 格式化为字符串
    current_time_str = now.strftime("%Y-%m-%d")
    past_24h_str = past_24h.strftime("%Y-%m-%d")
    print(f"当前时间: {current_time_str}")
    print(f"24小时前: {past_24h_str}")
    result = await handle_search({"query": "test query","date_from": past_24h_str, "categories": ["cs.AI", "cs.LG"]})
    #content = json.loads(result[0].text)
    #print(content["total_results"])
    #paper = content["papers"][0]
    #print(paper["id"])
    #print(paper["title"])
    if not result or len(result) == 0:
        print("没有找到符合条件的论文")
        return
    for item in result:
        try:
            content = json.loads(item.text)
            
            # 打印总结果数
            print(f"总结果数: {content.get('total_results', 0)}")
            
            # 检查是否有论文数据
            if "papers" not in content or len(content["papers"]) == 0:
                print("当前结果中没有论文数据")
                continue
                
            # 遍历所有论文
            for paper in content["papers"]:
                print("\n论文信息:")
                print(f"ID: {paper.get('id', 'N/A')}")
                print(f"标题: {paper.get('title', '无标题')}")
                # 可以继续打印其他字段
                print(f"作者: {', '.join(paper.get('authors', ['未知作者']))}")
                print(f"摘要: {paper.get('abstract', '无摘要')[:100]}...")  # 只显示前100字符
                print(f"开始下载论文")
                response = await handle_download({"paper_id": paper["id"]})
                #response = await handle_download({"paper_id": paper["id"], "check_status": True})
                #final_status = json.loads(response[0].text)
                #print(f"{final_status}")
                #if final_status["status"] == "success":
                #    print(f"论文下载完成") 
                for attempt in range(1, 10):
                    print(f"尝试 {attempt}/10 检查状态...")
                    response = await handle_download({
                        "paper_id": paper["id"],
                        "check_status": True
                    })
                    
                    final_status = json.loads(response[0].text)
                    print(f"当前状态: {final_status}")
                    
                    if final_status.get("status") == "success":
                        print("论文下载完成！")
                        paper_markdown_file = get_paper_path(paper["id"])
                        with open(paper_markdown_file, 'r', encoding='utf-8') as file:
                            first_line = file.read()
                            task = prompt +"\n"+first_line
                            #print(task)
                            try:
                                response = client.chat.completions.create(
                                    model="deepseek-chat",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful assistant"},
                                        {"role": "user", "content": task},
                                    ],
                                    stream=False
                                )
                                #print(response.choices[0].message.content)
                                content = "# "+paper["id"]+"\n"+response.choices[0].message.content + "\nhttps://arxiv.org/pdf/"+paper["id"]
                                with open('./summary.md', 'a', encoding='utf-8') as f:
                                    f.write(f"{content}\n") 
                            except Exception as e:
                                print(f"处理数据时发生错误: {str(e)}")
                                continue
                        break

                    if attempt < 10:
                        print(f"等待 {30} 秒后重试...")
                        await asyncio.sleep(30)
                
        except json.JSONDecodeError:
            print("错误: 无法解析JSON数据")
            continue
        except Exception as e:
            print(f"处理数据时发生错误: {str(e)}")
            continue



asyncio.run(main())