from strands import Agent
from strands.handlers.callback_handler import PrintingCallbackHandler
from AnalysisResult import Sentence
from typing import List

import json

class SummaryAgent:
    def __init__(self, config, model):
        self.agent = Agent(
            model=model,
            callback_handler=PrintingCallbackHandler(),
            system_prompt=(
                config["summary_instructions"]
            )
        )

    def summary(self, messages: List[Sentence]):
        needLLMSummary = []
        for msg in messages: 
            analysis = msg.AnalysisResult
            item = {
                "Subject": analysis.Subject,
                "Predicate": analysis.Predicate,
                "Object": analysis.Object,
            }
            needLLMSummary.append(item)
            
        json_str = json.dumps(needLLMSummary, indent=2, ensure_ascii=False)
        print(f"\nProcessing message: {json_str}")
        response = self.agent(json_str)   
        print(f"Total tokens: {response.metrics.accumulated_usage['totalTokens']}")
        print(f"Execution time: {sum(response.metrics.cycle_durations):.2f} seconds")
        print(f"Tools used: {list(response.metrics.tool_metrics.keys())}")
        return response