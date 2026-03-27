from env.environment import Environment
from env.models import Action

def medium_task(env: Environment):
    observation = env.reset()
    while observation.platform_metrics["step"] < 8:
        for post in observation.posts:
            if post.toxicity > 0.6:
                env.step(Action(action_type="delete", target_id=post.id))
            else:
                env.step(Action(action_type="ignore", target_id=post.id))
        observation = env.state()
    return 0.7 * (1 - observation.platform_metrics["toxicity_level"]) + 0.3 * observation.platform_metrics["engagement"]