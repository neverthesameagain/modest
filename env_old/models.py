from pydantic import BaseModel
from typing import List, Dict

class Post(BaseModel):
    id: int
    text: str
    toxicity: float
    user_id: int

class Observation(BaseModel):
    posts: List[Post]
    platform_metrics: Dict[str, float]

class Action(BaseModel):
    action_type: str  # "delete" or "ignore"
    target_id: int