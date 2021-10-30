from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import datetime 
from flask import Blueprint, jsonify, request 
import re 

tasks_bp = Blueprint("tasks",__name__, url_prefix=("/tasks" ))

@tasks_bp.route("", methods=["GET"])
def get_task():
    sort_query = request.args.get("sort")
    if sort_query == "desc":
        task = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
        task = Task.query.order_by(Task.title.asc())
    else:
        task = Task.query.all()
    
    task_response = [task.to_json() for task in task]
    return jsonify(task_response), 200


@tasks_bp.route("", methods=["POST"])
def post_task():
    if request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in \
        request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return {
            "task":{
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }
        }, 201


@tasks_bp.route("/<task_id>",methods=["GET","PUT","DELETE"])
def handle_task_id(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return ("", 404)

    if request.method == "GET":
        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : False if task.completed_at == None else True
            }
        }, 200

    if request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : False if task.completed_at == None else True
            }
        }, 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
            }), 200