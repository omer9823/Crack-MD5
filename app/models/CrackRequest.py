from pydantic import BaseModel
from typing import List

class CrackRequest(BaseModel):
    hashes: List[str]
    range_start: int
    range_end: int