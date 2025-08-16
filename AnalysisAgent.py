from clientInfo import clientInfo
from AnalysisResult import AnalysisResult, CommunicationMethod, Sentence
from typing import List
from spo_score import spo_score

import json

class AnalysisAgent:
    def __init__(self, LLM_Client):
        # Create an agent with tools from the strands-tools example tools package
        # as well as our custom letter_counter tool
        self.LLM_Client = LLM_Client
        self.messages = []
    def set_msg(self, message): 
        self.msg = message
        self.messages = [{"role": "system", "content": message.origin_text}]

    def analysis(self):
        results = []
        messages = []
        messages.append(self.messages[0])
        messages.append({"role": "user", "content": self.LLM_Client.get_config()["analysis_instructions"]})
        response = self.LLM_Client.talk_to_LLM_Json(messages)
        resp_answer = response.choices[0].message.content
        print(resp_answer)
        try:
                # 尝试将 response 转换为 AnalysisResult
                data = json.loads(str(resp_answer))
                result = AnalysisResult(**data)
                print(result.Subject)
                print(len(result.Subject))
                score = spo_score(
                        len(result.Subject),
                        len(result.Predicate),
                        len(result.Object),
                        len(result.Attributive),
                        len(result.Adverbial),
                        len(result.Complement),
                        len(result.Others)
                                    )
                # 收集结果
                self.msg.AnalysisResult = result
                self.msg.SPO_Score = score
                self.msg.Emotional_intensity=result.Emotional_intensity
                self.msg.CommunicationMethods=result.CommunicationMethods
                results.append(self.msg)
                
                # 打印结构化结果
                #print("Analysis Result:")
                #print(result.model_dump_json(indent=2))
                
        except Exception as e:
            print(f"Error processing message: {e}")
            results.append(None)
        
        return results

    def summary(self):
        messages = []
        messages.append(self.messages[0])
        messages.append(
            {"role": "user", "content": self.LLM_Client.get_config()["summary_instructions"]
        })
        summary_response = self.LLM_Client.talk_to_LLM(messages)
        return summary_response.choices[0].message.content

#    def summary(self):
#        self.messages.append(
#            {"role": "user", "content": self.LLM_Client.get_config()["summary_instructions"]
#        })
#        summary_response = self.LLM_Client.talk_to_LLM(self.messages)
#        return summary_response.choices[0].message.content
#def process_messages(self, messages: List[str]):
#        results = []
#        self.messages.append({"role": "system", "content": self.LLM_Client.get_config()["analysis_instructions"]})
#        for msg in messages:
#            print(f"\nProcessing message: {msg}")
#            self.messages.append({"role": "user", "content": msg})
#            # 调用 agent 处理消息
#            response = self.LLM_Client.talk_to_LLM_Json(self.messages)
#            resp_answer = response.choices[0].message.content
#            print(resp_answer)
#            self.messages.append({"role": "user", "content": resp_answer})
#            try:
                # 尝试将 response 转换为 AnalysisResult
#                data = json.loads(str(resp_answer))
#                result = AnalysisResult(**data)
#                print(result.Subject)
#                print(len(result.Subject))
#                score = spo_score(
#                        len(result.Subject),
#                        len(result.Predicate),
#                        len(result.Object),
#                        len(result.Attributive),
#                        len(result.Adverbial),
#                        len(result.Complement),
#                        len(result.Others)
#                                    )
                # 收集结果
#                Current_Sentence = Sentence(
#                    origin_text=msg,
#                    AnalysisResult=data,
#                    SPO_Score=score,
#                    Emotional_intensity=result.Emotional_intensity,
#                    CommunicationMethods= result.CommunicationMethods
#                )
#                results.append(Current_Sentence)
                
                # 打印结构化结果
#                print("Analysis Result:")
#                print(result.model_dump_json(indent=2))
                
#            except Exception as e:
#                print(f"Error processing message: {e}")
#                results.append(None)
        
#        return results

#def trim_json_output(content):
#    """
#    智能处理可能包含```json标记的内容：
#    1. 如果内容被```json ... ```包裹，则提取内部JSON部分
#    2. 否则保留原始内容
#    """
#    # 匹配 ```json 开头和 ``` 结尾的模式（允许前后空白）
#    pattern = r'^\s*```json\s*\n?(.*?)\n?\s*```\s*$'
#    match = re.fullmatch(pattern, content, re.DOTALL)
#    
#    if match:
#        # 提取json内容并去除首尾空白
#        return match.group(1).strip()
#    return content.strip()

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

