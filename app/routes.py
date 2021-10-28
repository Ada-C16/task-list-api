from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, request, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET","POST"])
def handle_tasks():
    if request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter_by(title=title_query)
        else:
            tasks = Task.query.all()
        
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()) 
        else:
            tasks = Task.query.all()
        
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
        return make_response(jsonify(tasks_response), 200)
    
    
    elif request.method == "POST":
        request_body = request.get_json()
        try: 
            new_task = Task(
                title = request_body["title"],
                description = request_body["description"],
                completed_at = request_body["completed_at"]
            )
        except:
            return make_response({"details": "Invalid data"}, 400)

        db.session.add(new_task)
        db.session.commit()

        return make_response({
            "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)
            }
        }, 201)


@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)
    if request.method == "GET":
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }
        }
    
    
    elif request.method == "PUT":
        form_data = request.get_json()
        if form_data.get("title"):
            task.title = form_data["title"]
        if form_data.get("description"):
            task.description = form_data["description"]
        if form_data.get("completed_at"):
            task.completed_at = form_data["completed_at"] 
        db.session.commit()
        return make_response({
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }
        }
        )


    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return make_response({
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'
    })

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)
    if request.method == "PATCH":
        
        from datetime import datetime
        task.completed_at = datetime.now()

        return make_response({
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }
        }
        )
@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def incomplete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)
    if request.method == "PATCH":
        task.completed_at = None

        return make_response({
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }
        }
        )