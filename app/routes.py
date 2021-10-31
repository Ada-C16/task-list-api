from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app import db


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def is_input_valid(number):
    try:
        int(number)
    except:
        return make_response(f"{number} is not an int!", 400)


def is_parameter_found(parameter_id):
    if is_input_valid(parameter_id) is not None:
        return is_input_valid(parameter_id)
    elif Task.query.get(parameter_id) is None:
        return make_response(f"{parameter_id} was not found!", 404)

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}),400
    new_task = Task(title = request_body["title"],
                    description=request_body["description"], 
                    completed_at=None
                    )

    db.session.add(new_task)
    db.session.commit()
    response_body = {}
    response_body["task"] = new_task.to_dict()

    return jsonify(response_body), 201


@tasks_bp.route("", methods=["GET"])
def read_tasks():
        tasks = Task.query.all()
        response_body = []
        for task in tasks:
            response_body.append(
                task.to_dict())
        
        return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_task(task_id):
    if is_parameter_found(task_id) is not None:
        return is_parameter_found(task_id)
    task = Task.query.get(task_id)
    task_response = {}
    task_response["task"] = task.to_dict()
    return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    if is_parameter_found(task_id) is not None:
        return is_parameter_found(task_id)

    task = Task.query.get(task_id)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    response_body = {}
    response_body["task"] = task.to_dict()
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["PATCH"])
def update_task_parameter(task_id):
    if is_parameter_found(task_id) is not None:
        return is_parameter_found(task_id)
    task = Task.query.get(task_id)
    request_body = request.get_json()
    if "title" in request_body:
        task.name = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    
    db.session.commit()
    return make_response(f"Task {task_id} successfully updated!", 200)


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    if is_parameter_found(task_id) is not None:
        return is_parameter_found(task_id)
    task = Task.query.get(task_id)
    task_title = task.title
    response_str = f'Task {task_id} "{task_title}" successfully deleted'

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "details": response_str
        }), 200
