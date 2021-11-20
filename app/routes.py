from flask import Blueprint, request, make_response, jsonify, abort
from app.models.task import Task
from app import db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# # Helper functions
def valid_int(number):
    try:
        id = int(number)
        return id 
    except:
        response_body = 'Invalid Data'
        abort(make_response(response_body,400))

def get_task_from_id(task_id):
    id = valid_int(task_id)
    selected_task = Task.query.filter_by(task_id=task_id).one_or_none()
    # Task not found
    if selected_task is None:
        abort(make_response("Not Found", 404))
    return selected_task

def valid_task(request_body):
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))
# #

# Get all tasks
@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_tasks():
    sort_tasks = request.args.get("sort")
    response_list = []

    # Sort task: by title, ascending
    if sort_tasks == "asc":
        task_objects = Task.query.order_by(Task.title.asc())
    # Sort task: by title descending
    elif sort_tasks == "desc":
                task_objects = Task.query.order_by(Task.title.desc())
    else:
        task_objects = Task.query.all()

    for task in task_objects:
        response_list.append(task.to_dict())
    return make_response(jsonify(response_list), 200)



# Get one task
@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_task(task_id):
    # selected_task = Task.query.filter_by(task_id=task_id).one_or_none()
    # # Task not found
    # if selected_task is None:
    #     abort(make_response("Not Found", 404))
    selected_task = get_task_from_id(task_id)
    response_body = {"task": selected_task.to_dict()}
    return make_response(response_body, 200)

# Create one task with error handlers
@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_task():
    request_body = request.get_json()
    valid_task(request_body)
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    response = {"task": new_task.to_dict()}
    return make_response(response, 201)

# Update task
@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    selected_task = get_task_from_id(task_id)
    request_body = request.get_json()
    if "title" in request_body:
        selected_task.title = request_body["title"]
    if "description" in request_body:
        selected_task.description = request_body["description"]
    
    db.session.commit()
    response_body = {"task": selected_task.to_dict()}
    return make_response(response_body, 200)

# Delete task
@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    selected_task = get_task_from_id(task_id)
    db.session.delete(selected_task)
    db.session.commit()
    response_body = {'details': f'Task {task_id} "{selected_task.title}" successfully deleted'}
    return make_response(response_body, 200)
