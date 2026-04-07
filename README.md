---
title: Modest Content Moderation
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---
# modest: Adaptive Content Moderation Under Uncertainty

`modest` is an award-winning, OpenEnv-compatible environment designed for simulating dynamic, real-world content moderation. The objective is to manage the organic flow of user toxicity by balancing short-term content removal against long-term community health.

## Environment Description & Motivation

Content moderation is rarely an isolated classification task. In real-world platforms, toxicity is contagious, and users build reputations. This environment simulates:
1. **Thread Infection Mechanic**: Ignored toxic posts escalate the "Thread Temperature", meaning innocent users become infected and start posting toxic content in retaliation.
2. **User Entities**: A persistent tracking of `Users` participating in the thread with visible `trust_score`s and hidden true motives (`propensity_to_toxicity`).
3. **Double Action Space**: The agent can now choose to `delete_post` (short-term fix) or `ban_user` (long-term cure) with massive reward penalties for falsely banning highly-trusted, innocent users.

The goal is to provide a fully contextual, realistic testbed for state-of-the-art LLM Agents.

## Setup & Usage

### 1. Run the Server (Hugging Face Space via Docker)
The environment executes as a persistent HTTP Server via FastAPI, built explicitly for Hugging Face Spaces.
```bash
docker build -t modest .
docker run -p 7860:7860 modest
```

### 2. Run the Evaluator Baseline
The inference reproduces the agent traversal over the Modest pipeline connecting via OpenAI client standards.
```bash
uv run inference.py
```

## Observation & Action Space

### Observation Definition
The observation returns an enriched context:
- `posts`: A collection of currently active user posts `[id, text, user_id]`. Note that true toxicity floats are intentionally hidden ensuring the agent uses linguistic intelligence.
- `users`: Community participants `[id, trust_score]`.
- `platform_metrics`: The current global `engagement` level and `thread_temperature`.

### Action Definition
The Agent returns a single action dict mapping to the `Action` Pydantic model:
- `{"action_type": "delete_post", "target_id": <post_id>}`: Culls immediate toxicity (+1 Reward).
- `{"action_type": "ban_user", "target_id": <user_id>}`: Eliminates instigator from posting (+5 Reward), but huge penalty if innocent high-trust user (-10 Reward).
- `{"action_type": "ignore", "target_id": 0}`: Disregards, inherently carrying risk of Thread Temperature escalation.

## Tasks and Graders

- **Easy**: `Clean the Queue` — Graded solely on final string toxicity parsing. Simple object clearing objective.
- **Medium**: `Surgical Precision` — Evaluated on establishing low final toxicity WITHOUT plummeting thread engagement (penalizes reckless blanket banning).
- **Hard**: `De-escalation Expert` — Scored strictly on the inverse variance of the `thread_temperature` overtime. Finding instigators proactively is mandatory to minimize variance.

## Baseline

Our standard baseline script executing zero-shot completions produces reproducible tracking logs conforming entirely to the required OpenEnv formatting framework:

**Current Baseline Metrics:**
- **Easy**: `0.57` - `0.94` (Model: gpt-4o)
- **Medium**: `0.42` - `0.80`
- **Hard**: `0.57` - `0.78`

## License
MIT License
