from pydantic import BaseModel

class CrackRequest(BaseModel):
    hash: str
    range_start: str
    range_end: str