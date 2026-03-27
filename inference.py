from env.environment import Environment
from env.models import Action
from tasks.easy import easy_task
from tasks.medium import medium_task
from tasks.hard import hard_task
import random

def baseline_agent(env):
    observation = env.reset()
    for _ in range(8):
        for post in observation.posts:
            action = Action(
                action_type="delete" if post.toxicity > 0.6 else "ignore",
                target_id=post.id
            )
            env.step(action)
        observation = env.state()
    return observation

def main():
    random.seed(42)
    env = Environment()

    # Run baseline agent
    final_observation = baseline_agent(env)

    # Calculate scores
    easy_score = easy_task(env)
    medium_score = medium_task(env)
    hard_score = hard_task(env)

    print("Final Toxicity:", final_observation.platform_metrics["toxicity_level"])
    print("Easy Score:", easy_score)
    print("Medium Score:", medium_score)
    print("Hard Score:", hard_score)

if __name__ == "__main__":
    main()