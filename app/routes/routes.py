from re import T
from flask import Blueprint, jsonify, make_response, request, abort
from app import db
from app.models.task import Task


task_bp = Blueprint("task", __name__,url_prefix="/tasks")

# Helper functions to validate if id is integer
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description="{Task not found}")

#routes that use GET method
@task_bp.route("", methods=["GET"])
def get_tasks():
    task_response=[]
    tasks = Task.query.all()

    for task in tasks:
        task_response.append(
            task.to_dict()
        )
    return jsonify(task_response),200

@task_bp.route("/<task_id>", methods=["GET"])

def get_task(task_id):
    task = get_task_from_id(task_id)

    return make_response(task.to_dict(),200)


#routes that use POST method
@task_bp.route("", methods=["POST"])
def create_task(): 
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return {"error": "incomplete request body"}, 400

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
    )

    db.session.add(new_task)
    db.session.commit()
    return make_response(new_task.to_dict(), 201)

#routes that use PATCH method
@task_bp.route("/<task_id>", methods=["PATCH"])
def update_task(task_id):
    task = get_task_from_id(task_id)
    request_body= request.get_json()

    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]

    db.session.commit()
    return jsonify(task.to_dict()), 200

#routes that use DELETE method
@task_bp.route("", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_from_id(task_id)

    db.session.delete(task)
    db.session.commit()
    return jsonify(task.to_dict()), 200
