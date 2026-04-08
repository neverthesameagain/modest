def grade(final_state, trajectory=None) -> float:
    """Medium: Surgical Precision. Balance toxicity removal with engagement."""
    if isinstance(final_state, dict):
        avg_tox = final_state.get("metadata", {}).get("avg_true_toxicity", 0.5)
        engagement = final_state.get("metadata", {}).get("engagement", 0.5)
    else:
        avg_tox = final_state.metadata.get("avg_true_toxicity", 0.5)
        engagement = final_state.metadata.get("engagement", 0.5)

    score = 0.5 * max(0.0, 1.0 - avg_tox) + 0.5 * max(0.0, engagement)
    # Clamp strictly within (0, 1) — validator rejects exact 0.0 or 1.0
    score = min(0.99, max(0.01, score))
    return float(score)