from typing import List
from pydantic import BaseModel
from enum import Enum

class CommunicationMethod(BaseModel):
    category: str
    fact_check_keywords: List[str]

class AnalysisResult(BaseModel):
    Subject: List[str]
    Predicate:  List[str]
    Object:  List[str]
    Attributive:  List[str]
    Adverbial:  List[str]
    Complement:  List[str]
    Others:  List[str]
    Emotional_intensity: int
    CommunicationMethods: List[CommunicationMethod]