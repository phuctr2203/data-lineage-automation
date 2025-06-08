from pydantic import BaseModel
from typing import List

class Triplet(BaseModel):
    entity: str
    relationship: str
    object: str

class TripletResponse(BaseModel):
    triplets: List[Triplet]