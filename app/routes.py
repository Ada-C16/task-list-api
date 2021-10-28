from app import db
from flask import Blueprint, request, make_response, jsonify
from app.models.task import Task

# DEFINE BLUEPRINT
tasks_list_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

#CREATE
@tasks_list_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(f"New task {new_task.title} successfully created!", 201)

#READ
@tasks_list_bp.route("", methods=["GET"])
def read_all_tasks():
    tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response)


#UPDATE
@tasks_list_bp.route("", methods=["PATCH"]) 
def update_task():
    pass


#DELETE
@tasks_list_bp.route("", methods=["DELETE"]) 
def delete_task():
    pass