# modest: Adaptive Content Moderation Under Uncertainty

modest is an OpenEnv-compatible environment designed for simulating real-world content moderation. The goal is to balance reducing toxicity and maintaining user engagement over time.

## Features
- Sequential decision-making environment
- Dynamic system evolution
- Deterministic tasks with graders

## Project Structure
```
- env/
  - environment.py
  - models.py
- tasks/
  - easy.py
  - medium.py
  - hard.py
- data/
  - comments.json
- inference.py
- openenv.yaml
- Dockerfile
- requirements.txt
- README.md
```

## How to Run
1. Build the Docker image:
   ```bash
   docker build -t modest .
   ```
2. Run the container:
   ```bash
   docker run modest
   ```

## Requirements
- Python 3.10
- Pydantic
- NumPy
- OpenAI
- FastAPI
- Uvicorn

## Tasks
1. **Easy**: Remove toxic content.
2. **Medium**: Balance toxicity and engagement.
3. **Hard**: Optimize long-term platform health.

## License
MIT License
