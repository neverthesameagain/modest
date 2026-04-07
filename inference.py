import os
import json
from openai import OpenAI
from server.modest_environment import ModestEnvironment
from env.models import Action
from tasks import easy, medium, hard

def main():
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    api_key = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy")
    task_name = os.getenv("MY_ENV_TASK", "easy")
    
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    env = ModestEnvironment()
    
    if task_name == "hard":
        grader = hard.grade
    elif task_name == "medium":
        grader = medium.grade
    else:
        grader = easy.grade
    
    obs = env.reset()
    print(f"[START] task={task_name} env=modest model={model_name}")
    
    trajectory = [obs]
    rewards = []
    
    done = False
    step = 0
    
    while not done and step < 8:
        step += 1
        
        users_info = "\n".join([f"User {u.id} - Trust Score: {u.trust_score:.2f}" for u in obs.users])
        posts_info = "\n".join([f"Post {p.id} by User {p.user_id}: {p.text}" for p in obs.posts])
        
        prompt = (
            "You are an AI Community Manager.\n"
            f"--- Active Users ---\n{users_info}\n\n"
            f"--- Active Posts ---\n{posts_info}\n\n"
            "Task: Manage the toxicity while keeping trusted users active.\n"
            "Options:\n"
            "1. {'action_type': 'ban_user', 'target_id': <user_id>} -> Stops the user from continuing to post toxicity. High penalty if user is innocent!\n"
            "2. {'action_type': 'delete_post', 'target_id': <post_id>} -> Deletes a toxic post.\n"
            "3. {'action_type': 'ignore', 'target_id': 0} -> Do nothing.\n"
            "Return EXACTLY ONE JSON action."
        )
        
        error_msg = "null"
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            action_data = json.loads(content)
            
            action_type = action_data.get("action_type", "ignore")
            target_id = int(action_data.get("target_id", 0))
            
            action_obj = Action(action_type=action_type, target_id=target_id)
            
            obs = env.step(action_obj)
            rewards.append(obs.reward)
            trajectory.append(obs)
            done = obs.done
            
            action_str = f"{action_type}('{target_id}')"
            print(f"[STEP] step={step} action={action_str} reward={obs.reward:.2f} done={str(done).lower()} error={error_msg}")
            
        except Exception as e:
            error_msg = str(e).replace("\n", " ")
            obs = env.step(Action(action_type="ignore", target_id=0))
            rewards.append(obs.reward)
            trajectory.append(obs)
            done = obs.done
            print(f"[STEP] step={step} action=error reward={obs.reward:.2f} done={str(done).lower()} error={error_msg}")
            
    score = grader(obs, trajectory)
    success = score > 0.0
    
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={step} score={score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    main()