from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request

task_list_bp = Blueprint("task_list", __name__, url_prefix="/tasks")

@task_list_bp.route("", methods=["POST"])
def valid_task_with_null():
    request_body = request.get_json()
    valid_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(valid_task)
    db.session.commit()

    return make_response(f"task: {valid_task.title}", 201)
   

#GETS when there is at least one saved task and get this response: 
@task_list_bp.route("/tasks", methods=["GET"])
def getting_saved_tasks():
    return [
    {
        "id": 1,
        "title": "Example Task Title 1",
        "description": "Example Task Description 1",
        "is_complete": false
    },
    {
        "id": 2,
        "title": "Example Task Title 2",
        "description": "Example Task Description 2",
        "is_complete": false
    }
    ]