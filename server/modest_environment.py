import uuid
import random
import json
import os
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from env.models import Action, Observation, Post, User
except ImportError:
    from ..env.models import Action, Observation, Post, User

class ModestEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid.uuid4()), step_count=0)
        self.posts_data = []
        
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "comments.json")
        try:
            with open(data_path, "r") as f:
                self.raw_data = json.load(f)
        except Exception:
            self.raw_data = []
            
        self.users_internal = {}
        self.active_posts = []
        self.true_toxicities = {}
        self.platform_metrics = {}
        self.post_id_counter = 0

    def get_comment_sample(self, toxic: bool) -> str:
        if not self.raw_data:
            return "Sample generic text"
            
        # Filter pool
        pool = []
        for x in self.raw_data:
            tox = float(x.get("toxicity", 0.0))
            if toxic and tox > 0.5:
                pool.append(x.get("comment_text", ""))
            elif not toxic and tox <= 0.5:
                pool.append(x.get("comment_text", ""))
                
        if not pool:
            return "Sample generic text"
        return random.choice(pool)

    def reset(self) -> Observation:
        self._state = State(episode_id=str(uuid.uuid4()), step_count=0)
        self.post_id_counter = 0
        
        # Initialize 5 users
        self.users_internal = {}
        for i in range(1, 6):
            # Propensity is hidden, trust_score is visible
            is_toxic_user = random.random() < 0.4
            propensity = random.uniform(0.6, 1.0) if is_toxic_user else random.uniform(0.0, 0.4)
            trust_score = random.uniform(0.1, 0.5) if is_toxic_user else random.uniform(0.7, 1.0)
            
            self.users_internal[i] = {
                "id": i,
                "propensity": propensity,
                "trust_score": trust_score,
                "banned": False
            }
            
        self.active_posts = []
        self.true_toxicities = {}
        
        self.platform_metrics = {
            "engagement": 1.0,
            "step": 0,
            "thread_temperature": 0.0
        }
        
        # Generate 3 initial posts
        self._generate_posts(3)
        return self._build_observation(reward=0.0, done=False)

    def _generate_posts(self, count=1):
        unbanned_users = [u for u in self.users_internal.values() if not u["banned"]]
        if not unbanned_users:
            return
            
        for _ in range(count):
            user = random.choice(unbanned_users)
            
            # The higher the thread temperature, the more likely the post is toxic
            temp = self.platform_metrics["thread_temperature"]
            effective_propensity = min(1.0, user["propensity"] + (temp * 0.3))
            
            is_toxic = random.random() < effective_propensity
            text = self.get_comment_sample(toxic=is_toxic)
            
            self.post_id_counter += 1
            pid = self.post_id_counter
            
            self.active_posts.append({
                "id": pid,
                "text": text,
                "user_id": user["id"]
            })
            self.true_toxicities[pid] = 1.0 if is_toxic else 0.0

    def step(self, action: Action) -> Observation:
        self._state.step_count += 1
        reward = 0.0
        
        target_id = action.target_id
        action_type = action.action_type
        
        if action_type == "delete_post":
            post_idx = next((i for i, p in enumerate(self.active_posts) if p["id"] == target_id), None)
            if post_idx is not None:
                tox = self.true_toxicities[target_id]
                self.active_posts.pop(post_idx)
                if tox > 0.5:
                    reward += 1.0
                    self.platform_metrics["thread_temperature"] = max(0.0, self.platform_metrics["thread_temperature"] - 0.2)
                else:
                    reward -= 1.0
                    self.platform_metrics["engagement"] -= 0.1
                    
        elif action_type == "ban_user":
            if target_id in self.users_internal and not self.users_internal[target_id]["banned"]:
                self.users_internal[target_id]["banned"] = True
                user = self.users_internal[target_id]
                
                # Delete all their active posts
                self.active_posts = [p for p in self.active_posts if p["user_id"] != target_id]
                
                if user["propensity"] > 0.5:
                    reward += 5.0
                    self.platform_metrics["thread_temperature"] = 0.0
                else:
                    reward -= 10.0
                    self.platform_metrics["engagement"] -= 0.4
                    
        elif action_type == "ignore":
            pass
            
        # Evolution Mechanics
        toxic_count = sum(1 for p in self.active_posts if self.true_toxicities[p["id"]] > 0.5)
        
        # If toxic posts are left ignored, temperature rises
        if toxic_count > 0:
            self.platform_metrics["thread_temperature"] = min(1.0, self.platform_metrics["thread_temperature"] + (toxic_count * 0.15))
        else:
            self.platform_metrics["thread_temperature"] = max(0.0, self.platform_metrics["thread_temperature"] - 0.1)

        # Generate new posts (1 or 2 new posts per step)
        if sum(1 for u in self.users_internal.values() if not u["banned"]) > 0:
            new_post_count = random.randint(1, 2)
            self._generate_posts(new_post_count)

        self.platform_metrics["step"] += 1
        done = self.platform_metrics["step"] >= 8
        
        return self._build_observation(reward=reward, done=done)

    def _build_observation(self, reward: float, done: bool) -> Observation:
        posts = [Post(id=p["id"], text=p["text"], user_id=p["user_id"]) for p in self.active_posts]
        users = [User(id=u["id"], trust_score=round(u["trust_score"], 2)) for u in self.users_internal.values() if not u["banned"]]
        
        if self.active_posts:
            avg_tox = sum(self.true_toxicities[p["id"]] for p in self.active_posts) / len(self.active_posts)
        else:
            avg_tox = 0.0
            
        return Observation(
            posts=posts,
            users=users,
            platform_metrics=self.platform_metrics,
            reward=reward,
            done=done,
            metadata={
                "avg_true_toxicity": avg_tox, 
                "engagement": self.platform_metrics["engagement"],
                "thread_temperature": self.platform_metrics["thread_temperature"]
            }
        )

    @property
    def state(self) -> State:
        return self._state
