from app.models.task import Task
from app import db
from flask import Blueprint, jsonify, make_response, request

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            has_complete = task.completed_at
            tasks_response.append(
                {
                    "description": task.description,
                    "id": task.task_id,
                    "is_complete": False if has_complete == None else has_complete,
                    "title": task.title,
                }
            )
        return jsonify(tasks_response)
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("Invalid Request", 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return "201 CREATED",201


@tasks_bp.route("/<task_id>", methods=["GET"])
def handle_one_task(task_id):
    task_id = int(task_id)
    task = Task.query.get_or_404(task_id)

    if request.method == "GET":
        task_response = []
        task_response.append(
            {
                "description": task.description,
                "id": task.task_id,
                "is_complete": task.completed_at,
                "title": task.title,
            }
        )

        return jsonify(task_response)


