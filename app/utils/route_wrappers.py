from functools import wraps
from flask import jsonify
from app.models.task import Task
from app.models.goal import Goal

def require_instance_or_404(endpoint):
    """
    Decorator to validate that a requested id of input data exists.
    Returns JSON and 404 if not found."""
    @wraps(endpoint) # Makes fn look like func to return
    def fn(*args, **kwargs):
        if "task_id" in kwargs:
            task_id = kwargs.get("task_id", None)
            task = Task.query.get(task_id)

            if not task:
                return jsonify(None), 404 # null

            kwargs.pop("task_id")
            return endpoint(*args, task=task, **kwargs)
        
        elif "goal_id" in kwargs:
            goal_id = kwargs.get("goal_id", None)
            goal = Goal.query.get(goal_id)

            if not goal:
                return jsonify(None), 404

            kwargs.pop("goal_id")
            return endpoint(*args, goal=goal, **kwargs)

    return fn
