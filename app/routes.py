from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request, make_response
from datetime import datetime
from sqlalchemy import desc
import os


tasks_bp = Blueprint("tasks", __name__, url_prefix ="/tasks")

@tasks_bp.route("", methods=["POST"])
def create_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400
        
    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"]
                    )
    db.session.add(new_task)
    db.session.commit()
    
    return make_response({"task": {"id":new_task.task_id, "title":new_task.title, "description":new_task.description, "is_complete":bool(new_task.completed_at)}}), 201

@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by("title")
    elif sort_query == "desc":
        tasks = Task.query.order_by(desc("title"))
    else:
        tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_single_task(task_id):  
    task = Task.query.get(task_id)
    if task:
        return {
            "task":{
                "id": task.task_id, 
                "title": task.title, 
                "description": task.description, 
                "is_complete": bool(task.completed_at)
                }}, 200
    else:
        return jsonify(None), 404

@tasks_bp.route("/<task_id>", methods=["PUT"])
def change_data(task_id):
    task = Task.query.get(task_id)
    form_data = request.get_json()
    
    if task:
        task.title = form_data["title"]
        task.description = form_data["description"]
        # task.completed_at = form_data["completed_at"]

        db.session.commit()
        return {
            "task":{
                "id": task.task_id, 
                "title": task.title, 
                "description": task.description, 
                "is_complete": bool(task.completed_at)
                }}
    else:
        return jsonify(None), 404

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_planet(task_id):
    """Defines an endpoint DELETE to delete planet out of existence"""
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        return {"details": "Task 1 \"Go on my daily walk 🏞\" successfully deleted"}
    else:
        return jsonify(None), 404