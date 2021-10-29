from app import db
from app.models import task
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort

task_bp = Blueprint('task', __name__, url_prefix="/tasks")

@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body or "moons" not in request_body:
        return {"details": "Invalid data"}, 400   

    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(new_task)
    db.session.commit()

    return make_response('Task {new_task.title} successfully created')

