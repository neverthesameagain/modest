def grade(final_state, trajectory=None) -> float:
    """Easy: Clean the Queue. Graded on final toxicity level."""
    if isinstance(final_state, dict):
        avg_tox = final_state.get("metadata", {}).get("avg_true_toxicity", 0.5)
    else:
        avg_tox = final_state.metadata.get("avg_true_toxicity", 0.5)

    score = max(0.0, 1.0 - avg_tox)
    # Clamp strictly within (0, 1) — validator rejects exact 0.0 or 1.0
    score = min(0.99, max(0.01, score))
    return float(score)