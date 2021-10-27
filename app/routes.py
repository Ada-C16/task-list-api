from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task

# Create tasks blueprint
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []

        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            })
        return jsonify(tasks_response)
    
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in \
            request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400
        
        new_task = Task(
            title= request_body["title"],
            description= request_body["description"],
            completed_at= request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return {
            "task": {
                "id": 1,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False
                }
        }, 201