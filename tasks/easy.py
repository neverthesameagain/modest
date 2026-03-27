from env.environment import Environment
from env.models import Action

def easy_task(env: Environment):
    observation = env.reset()
    while observation.platform_metrics["step"] < 8:
        for post in observation.posts:
            if post.toxicity > 0.6:
                env.step(Action(action_type="delete", target_id=post.id))
            else:
                env.step(Action(action_type="ignore", target_id=post.id))
        observation = env.state()
    return 1 - observation.platform_metrics["toxicity_level"]