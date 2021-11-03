import os
import requests
from app.models.task import Task
from app.models.goal import Goal


def get_model_and_label(bp_name, no_label=False):
    bps = {
        "tasks": (Task, "task"),
        "goals": (Goal, "goal"),
    }

    return bps[bp_name][0] if no_label else bps[bp_name]
