from pydantic import Field
from typing import List
from pydantic import BaseModel

class IsQueryAboutOrder(BaseModel):
    is_query_about_order: bool

class IsLanguageOfUserIsOffensive(BaseModel):
    is_user_use_negative_words: List[bool]=Field(default_factory=list)
    is_user_use_offensive_language: List[bool] =Field(default_factory=list)

class IsOutputPolitical(BaseModel):
    contains_political_content:bool
    political_reference_found:str