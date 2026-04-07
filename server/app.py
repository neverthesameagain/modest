from fastapi import FastAPI
from server.modest_environment import ModestEnvironment

app = FastAPI()
env = ModestEnvironment()

@app.get("/")
def read_root():
    return {"status": "ok", "environment": "modest"}


@app.get("/reset")
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
