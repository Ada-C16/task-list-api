from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
import requests

task_bp=Blueprint("tasks", __name__, url_prefix="/tasks")

@task_bp.route("", methods=["GET", "POST"])
def all_tasks():
    task_list = []
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks=Task.query.order_by(Task.title.asc())
        elif sort_query =="desc":
            tasks=Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at is None else True
            })
        return jsonify(task_list)

    elif request.method =="POST":
        request_body = request.get_json()
        
        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            return  {"details": "Invalid data"},400

        new_task = Task(title=request_body["title"], 
            description=request_body["description"], 
            completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
        
        response_body = {'task': {
            "id": new_task.id, 
            "title": new_task.title, 
            "description": new_task.description, 
            "is_complete": False if new_task.completed_at is None else True}}


        return response_body, 201
    
@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method =="GET":
        if task is None:
            return make_response("", 404)
        return make_response({
            "task":{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": False if task.completed_at is None else True
                }
        }, 200)

    elif request.method == "PUT":
        if task is None:
            return make_response("", 404)
        form_data = request.get_json()

        task.title=form_data["title"]
        task.description = form_data["description"]
        # new_task = jsonify(task)
        response_body={"task": {"id": task.id, "title": task.title, "description": task.description, "is_complete": False if task.completed_at is None else True}}

        db.session.commit()
        return response_body, 200

    elif request.method =="DELETE":
        if task is None:
            return make_response("", 404)
        db.session.delete(task)
        db.session.commit()
        return make_response({"details":f'Task {task.id} "{task.title}" successfully deleted'}, 200)

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task=Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    
    db.session.commit()
    task.completed_at=True
    response_body={"task": {"id": task.id, "title": task.title, "description": task.description, "is_complete": False if task.completed_at is None else True}}
    r = requests.post(url="/<chat.postMessage>", channel="task-notifications", text=f'Someone completed the task {task.title}')
    return response_body, 200
    return r


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task=Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    db.session.commit()
    task.completed_at=None
    response_body={"task": {"id": task.id, "title": task.title, "description": task.description, "is_complete": False if task.completed_at is None else True}}
    
    return response_body, 200