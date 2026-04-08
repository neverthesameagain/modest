from fastapi import FastAPI
from server.modest_environment import ModestEnvironment

app = FastAPI()
env = ModestEnvironment()

@app.get("/")
def read_root():
    return {"status": "ok", "environment": "modest"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metadata")
def metadata():
    return {
        "name": "modest",
        "description": "Adaptive Content Moderation Under Uncertainty",
        "version": "1.0.0"
    }

@app.get("/schema")
def schema():
    from env.models import Action, Observation
    from openenv.core.env_server.types import State
    return {
        "action": Action.model_json_schema(),
        "observation": Observation.model_json_schema(),
        "state": State.model_json_schema()
    }


@app.post("/reset")
def reset():
    return env.reset()


@app.get("/state")
def state():
    return env.state()

@app.post("/step")
def step(action: dict):
    from env.models import Action
    action_obj = Action(**action)
    return env.step(action_obj)

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
