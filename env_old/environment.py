from pydantic import BaseModel
from typing import List, Dict, Tuple
import random
import json

with open("data/comments.json") as f:
    DATA = json.load(f)

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

class Environment:
    def __init__(self):
        self.posts = []
        self.platform_metrics = {
            "toxicity_level": 0.0,
            "engagement": 1.0,
            "step": 0
        }
        self.seed = 42
        random.seed(self.seed)

    def reset(self) -> Observation:
        self.posts = [
            Post(id=i, text=f"Post {i}", toxicity=random.uniform(0, 1), user_id=random.randint(1, 100))
            for i in range(10)
        ]
        self.platform_metrics = {
            "toxicity_level": sum(post.toxicity for post in self.posts) / len(self.posts),
            "engagement": 1.0,
            "step": 0
        }
        return self.state()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        reward = 0.0
        if action.action_type == "delete":
            post = next((p for p in self.posts if p.id == action.target_id), None)
            if post:
                self.posts.remove(post)
                if post.toxicity > 0.6:
                    reward += 1.0
                else:
                    reward -= 1.0
                self.platform_metrics["engagement"] -= 0.1
        elif action.action_type == "ignore":
            post = next((p for p in self.posts if p.id == action.target_id), None)
            if post and post.toxicity > 0.6:
                reward -= 1.0

        # Update toxicity and engagement
        if self.posts:
            self.platform_metrics["toxicity_level"] = sum(post.toxicity for post in self.posts) / len(self.posts)
        else:
            self.platform_metrics["toxicity_level"] = 0.0

        self.platform_metrics["step"] += 1

        # Simulate toxicity evolution
        for post in self.posts:
            post.toxicity = min(1.0, post.toxicity + random.uniform(0, 0.1))

        done = self.platform_metrics["step"] >= 8
        return self.state(), reward, done, {}

    def state(self) -> Observation:
        return Observation(posts=self.posts, platform_metrics=self.platform_metrics)