from strands import Agent
from strands.handlers.callback_handler import PrintingCallbackHandler
from deepSeekmodel import DeepSeekModel
from AnalysisResult import AnalysisResult, CommunicationMethod
from typing import List

import yaml
import logging
import os
import json

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

logging.getLogger("strands").setLevel(logging.DEBUG)

model = DeepSeekModel(
    api_key=os.environ["API_KEY"],
    base_url="https://api.deepseek.com",
    model_id="deepseek-chat",
)

with open("config.yaml", "r", encoding="utf-8") as f:
     config = yaml.safe_load(f)

# Create an agent with tools from the strands-tools example tools package
# as well as our custom letter_counter tool
agent = Agent(
    model=model,
    callback_handler=PrintingCallbackHandler(),
    system_prompt=(
        config["analysis_instructions"]
    )
)

# Ask the agent a question that uses the available tools
messages = [
    "云原生时代中，Kubernetes 已成为资源管理的事实标准。",
    "如今，在 AI 大模型蓬勃发展的背景下，基于 K8S 的 AI 基础设施面临哪些独特挑战？",
    "本文将从计算、存储、网络、调度这四大核心要素出发，分析运行 AI 大模型的 K8s 集群与普通 K8s 集群的区别，探讨构建高效 AI on K8S 平台的核心竞争力。",
    "大模型热潮兴起时，云原生体系已趋成熟，当前绝大多数AI基础设施都选择 Kubernetes 作为底层的资源管理平台。K8s 已在众多领域（大数据、互联网、生物医药、金融、游戏等）广泛应用。"
]

def process_messages(messages: List[str], agent):
    results = []
    for msg in messages:
        print(f"\nProcessing message: {msg}")
        
        # 调用 agent 处理消息
        response = agent(msg)
        
        # 打印基础统计信息
        print(f"Total tokens: {response.metrics.accumulated_usage['totalTokens']}")
        print(f"Execution time: {sum(response.metrics.cycle_durations):.2f} seconds")
        print(f"Tools used: {list(response.metrics.tool_metrics.keys())}")
        
        try:
            # 尝试将 response 转换为 AnalysisResult
            data = json.loads(str(response))
            result = AnalysisResult(**data)
            
            # 收集结果
            results.append(result)
            
            # 打印结构化结果
            print("Analysis Result:")
            print(result.model_dump_json(indent=2))
            
        except Exception as e:
            print(f"Error processing message: {e}")
            results.append(None)
    
    return results

analysis_results = process_messages(messages, agent)

#response = agent(message)
#print(response)
#print(f"Total tokens: {response.metrics.accumulated_usage['totalTokens']}")
#print(f"Execution time: {sum(response.metrics.cycle_durations):.2f} seconds")
#print(f"Tools used: {list(response.metrics.tool_metrics.keys())}")
#data = json.loads(str(response))
#print(data)
#result = AnalysisResult(**data)
#print(result.model_dump_json(indent=2))  # ensure_ascii=False显示中文

#result = agent.structured_output(AnalysisResult, message)
#print(result)

