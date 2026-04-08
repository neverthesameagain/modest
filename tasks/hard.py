def grade(final_state, trajectory=None) -> float:
    """Hard: De-escalation Expert. Minimize toxicity, preserve engagement, stabilize temperature."""
    if isinstance(final_state, dict):
        avg_tox = final_state.get("metadata", {}).get("avg_true_toxicity", 0.5)
        engagement = final_state.get("metadata", {}).get("engagement", 0.5)
    else:
        avg_tox = final_state.metadata.get("avg_true_toxicity", 0.5)
        engagement = final_state.metadata.get("engagement", 0.5)

    stability = 1.0
    if trajectory:
        temps = []
        for obs in trajectory:
            if isinstance(obs, dict):
                temps.append(obs.get("metadata", {}).get("thread_temperature", 0.0))
            else:
                temps.append(obs.metadata.get("thread_temperature", 0.0))

        if len(temps) > 1:
            mean = sum(temps) / len(temps)
            variance = sum((x - mean) ** 2 for x in temps) / len(temps)
            stability = max(0.0, 1.0 - (variance * 4))

    score = 0.3 * max(0.0, 1.0 - avg_tox) + 0.3 * max(0.0, engagement) + 0.4 * stability
    # Clamp strictly within (0, 1) — validator rejects exact 0.0 or 1.0
    score = min(0.99, max(0.01, score))
    return float(score)