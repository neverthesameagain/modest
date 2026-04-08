"""
Grader module for the Modest content moderation environment.

Each grader evaluates agent performance on a specific task variant.
All scores are clamped strictly within (0, 1).
"""

from tasks import TASKS
from tasks.easy import grade as grade_easy
from tasks.medium import grade as grade_medium
from tasks.hard import grade as grade_hard

# Re-export for direct import
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}

def get_grader(task_name: str):
    """Return the grading function for a task name."""
    return GRADERS.get(task_name, grade_easy)
