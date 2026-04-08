from tasks.easy import grade as _grade_easy
from tasks.medium import grade as _grade_medium
from tasks.hard import grade as _grade_hard


class Task:
    """Minimal task wrapper expected by the hackathon validator."""
    def __init__(self, task_id: str, description: str, difficulty: str, grade_fn):
        self.id = task_id
        self.name = task_id
        self.description = description
        self.difficulty = difficulty
        self._grade_fn = grade_fn

    def grade(self, state, trajectory=None) -> float:
        return self._grade_fn(state, trajectory)


TASKS = [
    Task(
        task_id="easy",
        description="Clean the Queue — Graded solely on final toxicity level.",
        difficulty="easy",
        grade_fn=_grade_easy,
    ),
    Task(
        task_id="medium",
        description="Surgical Precision — Balance toxicity removal with engagement.",
        difficulty="medium",
        grade_fn=_grade_medium,
    ),
    Task(
        task_id="hard",
        description="De-escalation Expert — Minimize toxicity, preserve engagement, stabilize temperature.",
        difficulty="hard",
        grade_fn=_grade_hard,
    ),
]
