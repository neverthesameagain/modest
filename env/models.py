from openenv.core.env_server.types import Action as BaseAction, Observation as BaseObservation
from pydantic import Field, BaseModel
from typing import List, Dict

class User(BaseModel):
    id: int
    trust_score: float

class Post(BaseModel):
    id: int
    text: str
    user_id: int

class Observation(BaseObservation):
    posts: List[Post]
    users: List[User]
    platform_metrics: Dict[str, float]

class Action(BaseAction):
    action_type: str = Field(..., description="'delete_post', 'ban_user', or 'ignore'")
    target_id: int
