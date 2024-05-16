from typing import List
from pydantic import BaseModel

class PositionInfo(BaseModel):
    company: str
    position: str
    job_post_urls: List[str]

class PositionInfoList(BaseModel):
    positions: List[PositionInfo]

class NamedUrl(BaseModel):
    name: str
    url: str 
