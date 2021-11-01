import re

from werkzeug.datastructures import HeaderSet
from app import db
from app.models.task import Task
from flask import Blueprint, request, jsonify

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400
        new_task = Task(
            title= request_body["title"],
            description= request_body["description"],
            completed_at = request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()
        
        response = {}
        # posted_task = Task.query.all()
        response["task"] = {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.is_complete
        }
        return jsonify(response), 201
    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query:
            if sort_query == "asc":
                tasks = Task.query.order_by(Task.title).all()
            elif sort_query == "desc":
                tasks = Task.query.order_by(Task.title.desc()).all()
        else: 
            tasks = Task.query.all()
        
        response_body = []
        for task in tasks:
            response_body.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            })
        return jsonify(response_body), 200

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(), 404

    if request.method == "GET":
        response = {}
        response["task"] = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        return jsonify(response), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        db.session.commit()
        
        response_body = {}
        response_body["task"] = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        return jsonify(response_body), 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = {
            "details": f"Task {task.id} \"{task.title}\" successfully deleted"
        }
        return jsonify(response_body), 200