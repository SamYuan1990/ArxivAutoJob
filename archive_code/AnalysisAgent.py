from clientInfo import clientInfo
from AnalysisResult import AnalysisResult, CommunicationMethod, Sentence
from typing import List
from spo_score import spo_score

import json
import logging

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
        #results = []
        messages = []
        messages.append(self.messages[0])
        messages.append({"role": "user", "content": self.LLM_Client.get_config()["analysis_instructions"]})
        response = self.LLM_Client.talk_to_LLM_Json(messages)
        resp_answer = response.choices[0].message.content
        logging.info(str(resp_answer))
        try:
                # 尝试将 response 转换为 AnalysisResult
                data = json.loads(str(resp_answer))
                result = AnalysisResult(**data)
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
                
        except Exception as e:
            logging.info(f"Error processing message: {e}")            
        
        return self.msg

    def summary(self):
        messages = []
        messages.append(self.messages[0])
        messages.append(
            {"role": "user", "content": self.LLM_Client.get_config()["summary_instructions"]
        })
        self.msg.summary = self.LLM_Client.talk_to_LLM(messages).choices[0].message.content
        return self.msg
