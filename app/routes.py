from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task
from app import db

# assign tasks_bp to the new Blueprint instance
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def post_one_task():
    request.method == "POST"
    request_body = request.get_json()
    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(new_task)
    db.session.commit()
    # using is_completed to hold Boolean value of datetime which is the data type
    # for new_task.completed_at
    is_completed = new_task.completed_at is not None
    return make_response({"task": {"id": new_task.task_id,
                                    "title": new_task.title,
                                    "description": new_task.description,
                                    "is_complete": is_completed}})

