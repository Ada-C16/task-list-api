from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from sqlalchemy import desc

tasks_bp = Blueprint("task", __name__, url_prefix="/tasks")

def make_task_dict(task):
    task_dict = {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": True  
    }

    if not task.completed_at:
        task_dict["is_complete"] = False  

    return task_dict 

@tasks_bp.route("", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query:
            if sort_query == "asc":
                tasks = Task.query.order_by("title") 
            else:
                tasks = Task.query.order_by(desc("title")) 
        else: 
            tasks = Task.query.all()

        tasks_response = [make_task_dict(task) for task in tasks]     
        return jsonify(tasks_response), 200

    elif request.method == "POST": 
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body\
        or "completed_at" not in request_body:
            return { "details" : "Invalid data" }, 400

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()
        return { "task" : make_task_dict(new_task) }, 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)
    
    if request.method == "GET":
        return { "task" : make_task_dict(task) }, 200

    elif request.method == "PUT":
        request_data = request.get_json()
        task.title = request_data["title"]
        task.description = request_data["description"]
        if not task.completed_at:
            completed_or_not = False
        else:
            completed_or_not = True 

        db.session.commit()

        task_dict = {
                "id": task.task_id,
                "title": request_data["title"],
                "description": request_data["description"],
                "is_complete": completed_or_not 
            }

        return { "task" : task_dict }, 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return { "details" : f"Task {task.task_id} \"{task.title}\" successfully deleted" }, 200

