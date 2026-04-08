def grade(final_state, trajectory=None) -> float:
    """Hard: De-escalation Expert. Minimize toxicity, preserve engagement, stabilize temperature."""
    avg_tox = 0.5
    engagement = 0.5
    try:
        if isinstance(final_state, dict):
            avg_tox = final_state.get("metadata", {}).get("avg_true_toxicity", 0.5)
            engagement = final_state.get("metadata", {}).get("engagement", 0.5)
        elif hasattr(final_state, "metadata"):
            if isinstance(final_state.metadata, dict):
                avg_tox = final_state.metadata.get("avg_true_toxicity", 0.5)
                engagement = final_state.metadata.get("engagement", 0.5)
            else:
                avg_tox = getattr(final_state.metadata, "avg_true_toxicity", 0.5)
                engagement = getattr(final_state.metadata, "engagement", 0.5)
    except Exception:
        pass

    stability = 1.0
    if trajectory:
        temps = []
        for obs in trajectory:
            try:
                if isinstance(obs, dict):
                    temps.append(obs.get("metadata", {}).get("thread_temperature", 0.0))
                elif hasattr(obs, "metadata"):
                    if isinstance(obs.metadata, dict):
                        temps.append(obs.metadata.get("thread_temperature", 0.0))
                    else:
                        temps.append(getattr(obs.metadata, "thread_temperature", 0.0))
            except Exception:
                temps.append(0.0)

        if len(temps) > 1:
            mean = sum(temps) / len(temps)
            variance = sum((x - mean) ** 2 for x in temps) / len(temps)
            stability = max(0.0, 1.0 - (variance * 4))

    score = 0.3 * max(0.0, 1.0 - avg_tox) + 0.3 * max(0.0, engagement) + 0.4 * stability
    # Clamp strictly within (0, 1) — validator rejects exact 0.0 or 1.0
    score = min(0.99, max(0.01, score))
    return float(score)