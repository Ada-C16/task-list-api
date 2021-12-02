from flask import Blueprint, request, jsonify
from flask.helpers import make_response
from app import db
from app.models.goal import Goal
from app.models.task import Task

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# Create a Task: Valid Task With null completed_at
# As a client, I want to be able to make a POST 
# request to /tasks with the following HTTP request body

@task_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    request_body = request.get_json()
    response_body = []

    if request.method == "GET":
        tasks = Task.query.all()
        #return tasks
        # if tasks is None:
        #     return {
        #         "details" : "You have no scheduled tasks"
        #     }, 400
        
        # else:
        for task in tasks:
            response_body.append({
                "id" : task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }) 
        return jsonify(response_body)

    elif request.method == "POST":
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": "Invalid data"
            }, 400

        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )
        #try:
        db.session.add(new_task)
        db.session.commit()
        # except:
        #     pass
        #     return # error

        return {
            "task" : {
                "id" : new_task.id,
                "title" : new_task.title,
                "description" : new_task.description,
                "is_complete" : False
            }
        }, 201

@task_bp.route("/<task_id>", methods=["PUT", "GET", "DELETE"])
def handle_specific_task(task_id):
    
    task = Task.query.get(task_id)
    if task is None:
        pass

    if request.method == "GET":
        return {
            "task" : {
                "id" : task.id,
                "description" : task.description,
                "title": task.title,
                "is_complete" : False
            },
        }, 200

    elif request.method == "PUT":
        form_data = request.get_json()

        task.description = form_data["description"]
        task.title = form_data["title"]

        db.session.commit()
        return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
        }
        }, 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {
            "details" : f'Task {task.id} "{task.title}" successfully deleted'
            }, 200