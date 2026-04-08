import os
import json
from openai import OpenAI
from server.modest_environment import ModestEnvironment
from env.models import Action
from tasks import TASKS
from tasks import easy, medium, hard

GRADERS = {"easy": easy.grade, "medium": medium.grade, "hard": hard.grade}

def run_task(client, model_name, task_name, grader):
    """Run a single task and return the score."""
    env = ModestEnvironment()
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
    return score

def main():
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    api_key = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy")
    
    # Run all tasks if no specific task is specified (hackathon parser expectation)
    task_name = os.getenv("MODEST_TASK") or os.getenv("TASK_ID", "all")
    
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    
    if task_name == "all":
        # Evaluator runs this script once and needs to see 3 tasks with graders logged
        for t in TASKS:
            run_task(client, model_name, t.id, t.grade)
    else:
        grader = GRADERS.get(task_name, easy.grade)
        run_task(client, model_name, task_name, grader)

if __name__ == "__main__":
    main()