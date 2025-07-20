from pydantic import BaseModel

class CrackRequest(BaseModel):
    hash: str
    range_start: int
    range_end: int