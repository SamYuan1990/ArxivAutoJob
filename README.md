# ArxivAutoJob

一个高度自动化、采用流式处理架构的arXiv论文处理工具。它能够自动搜索、下载、分析AI/ML领域的最新论文，并生成RSS和Markdown格式的报告。

## 功能特性

- **流式处理架构**: 从下载、转换到AI分析，各阶段采用异步队列连接，实现真正的并发处理，大大缩短了获取分析结果的时间。
- **稳健的错误处理**: 通过进程隔离处理PDF转换，即使个别文件损坏导致底层库崩溃，主程序也能继续运行，不会中断。
- **灵活的配置**: 
    - 通过命令行参数自定义搜索的论文分类、数量和时间范围。
    - 通过环境变量配置任何兼容OpenAI的AI模型服务。
- **多样化输出**: 
    - 生成 `rss.xml` 文件，便于通过RSS阅读器订阅。
    - 生成 `summary.md` 文件，包含所有论文的摘要，便于快速阅读和归档。
- **现代化的文件名管理**: 输出文件以 `[ID] - [Title].ext` 的格式命名，清晰易读。

## 安装与配置

1.  **安装依赖**: 
    ```bash
    pip install -r requirements.txt
    ```

2.  **配置AI模型 (环境变量)**:
    在您的环境中设置以下变量，以指向您选择的AI模型服务。
    ```bash
    # 您的API Key
    export OPENAI_API_KEY="your_api_key"
    
    # API服务的Base URL (例如，本地模型或第三方服务)
    export OPENAI_API_BASE="https://api.deepseek.com"
    
    # 要使用的模型名称
    export OPENAI_MODEL="deepseek-chat"
    ```

## 使用方法

通过 `new_main.py` 脚本运行程序。您可以通过命令行参数自定义其行为。

**基本用法 (使用默认参数):**
```bash
python main.py
```

**高级用法 (自定义参数):**
```bash
# 搜索计算机视觉(cs.CV)分类下，过去3天内最多10篇论文
python main.py --categories cs.CV --days-back 3 --max-results 10

# 搜索多个分类
python main.py --categories cs.RO cs.CL
```

### 可用参数

- `--categories`: （可多个）要搜索的arXiv分类，默认为 `cs.AI cs.LG cs.CV cs.CL`。
- `--max-results`: （整数）本次运行处理的最大论文数，默认为 `50`。
- `--days-back`: （整数）从今天起向前搜索的天数，默认为 `7`。

## 架构与组件

- `new_main.py`: 项目的主入口，负责解析命令行参数并启动流水线。
- `pipeline_processor.py`: 核心的流式处理控制器，通过异步队列调度下载、转换和分析任务。
- `report_generator.py`: 报告生成器，在所有论文处理完毕后，负责生成 `rss.xml` 和 `summary.md`。
- `paper_downloader.py`: 负责论文的下载和PDF到Markdown的转换。
- `safe_converter.py`: 在隔离的子进程中运行的PDF转换器，确保主程序的稳定。
- `ai_analyzer.py`: 调用AI模型服务，对论文内容进行分析和JSON结构化提取。
- `arxiv_search.py`: 使用官方`arxiv`库搜索论文。

## 输出文件

所有生成的文件都位于 `download/` 目录下。

- `[ID] - [Title].pdf`: 下载的原始PDF文件。
- `[ID] - [Title].md`: 从PDF转换的Markdown文件。
- `[ID] - [Title]_analysis.json`: AI分析后提取出的结构化JSON数据。
- `rss.xml`: 用于RSS订阅的XML文件。
- `summary.md`: 包含所有论文分析结果的Markdown报告。
