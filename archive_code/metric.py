from prometheus_client import REGISTRY, Counter, Summary
from prometheus_client.exposition import generate_latest

import logging

LLM_RESPONSE_TIME = Summary(
    "llm_response_time_seconds", "Time spent processing LLM requests"
)
LLM_TOKENS_USED = Counter(
    "llm_tokens_used_total", "Total tokens used by LLM", ["model", "type"]
)

def print_metrics():
    try:
        # 获取所有指标数据并解码为UTF-8字符串
        metrics_data = generate_latest(REGISTRY).decode("utf-8")
        logging.info("\n=== Current Prometheus Metrics ===")
        logging.info(metrics_data)
        logging.info("=================================\n")
    except Exception as e:
        logging.info(f"Error printing metrics: {str(e)}")
