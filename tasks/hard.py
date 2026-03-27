from env.environment import Environment
from env.models import Action
import numpy as np

def hard_task(env: Environment):
    observation = env.reset()
    toxicity_values = []

    while observation.platform_metrics["step"] < 8:
        toxicity_values.append(observation.platform_metrics["toxicity_level"])
        for post in observation.posts:
            if post.toxicity > 0.6:
                env.step(Action(action_type="delete", target_id=post.id))
            else:
                env.step(Action(action_type="ignore", target_id=post.id))
        observation = env.state()

    stability = 1 - np.var(toxicity_values)
    return (
        0.4 * (1 - observation.platform_metrics["toxicity_level"])
        + 0.3 * observation.platform_metrics["engagement"]
        + 0.3 * stability
    )