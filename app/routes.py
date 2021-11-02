from flask import abort, Blueprint, jsonify, request, make_response
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_data = request.get_json()

    if "title" not in request_data or "description" not in request_data \
        or "completed_at" not in request_data:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title=request_data["title"], description=request_data["description"],
                completed_at=request_data["completed_at"])
    
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201

    # return f"Task {new_task.title} created", 201
    

@tasks_bp.route("", methods=["GET"])
def list_all_tasks():
    tasks_response = []
    #Can't be jsonified
    tasks = Task.query.all()
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT"])
def handle_task(task_id):
    print(f"handle task {task_id}")
    print(f"Request Method {request.method}")
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200
        
    elif request.method == "PUT":
        input_data = request.get_json()
        input_data = sanitize_data(input_data)
        task.title = input_data["title"]
        task.description = input_data["description"]
        db.session.commit()

        return jsonify({"task": task.to_dict()}), 200

def sanitize_data(input_data):
    data_types = {"title": str, "description": str}
    for name, val_type in data_types.items():
        try:
            val = input_data[name]
            type_test = val_type(val)
        except Exception as e:
            abort(400, "Bad Data")
    return input_data


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    print(f"Delete{task_id}")
    try:
        task_id = int(task_id)
    except ValueError:
        return 404
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        response_string = f'Task {task_id} "{task.title}" successfully deleted'

        return jsonify({
            "details": response_string
            }), 200


    else:
        return make_response("", 404)