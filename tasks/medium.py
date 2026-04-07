def grade(final_state, trajectory=None) -> float:
    if isinstance(final_state, dict):
        avg_tox = final_state.get("metadata", {}).get("avg_true_toxicity", 0.0)
        engagement = final_state.get("metadata", {}).get("engagement", 1.0)
    else:
        avg_tox = final_state.metadata.get("avg_true_toxicity", 0.0)
        engagement = final_state.metadata.get("engagement", 1.0)
        
    score = 0.5 * max(0.0, 1.0 - avg_tox) + 0.5 * max(0.0, engagement)
    return float(score)