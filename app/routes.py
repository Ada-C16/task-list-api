from app import db
from app.models.task import Task
from app.models.goal import Goal 
from flask import Blueprint, jsonify, make_response, request 

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    # does the 404 response go here, guard clause 
    if request.method == "GET":
        tasks = Task.query.all()    
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id" : task.id,
                "title" : task.title,
                "description" : task.description,
                "completed_at" : task.completed_at,
            })

        return jsonify(tasks_response), 200
    
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response("400 Bad Request")
        
        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        task = {
            "title" : new_task.title,
            "description" : new_task.description,
            "id" : new_task.id
        }

        return make_response("201 CREATED")
    
