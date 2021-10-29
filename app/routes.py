from app import db
from app.models import task
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort

task_bp = Blueprint('task', __name__, url_prefix="/tasks")


''' POST task  - this function handles the creation of a task.
    it requests "title", "description" and "completed_at" values to be to successful
'''
@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400   

    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(new_task)
    db.session.commit()

    return make_response(f'Task was "{new_task.title}" successfully created')


'''
        GET tasks - this function reads all tasks from databases
                - this function handles searches of tasks by: title
'''
@task_bp.route("", methods=["GET"])
def read_all_tasks():

    task_title_query = request.args.get("title")
    task_response = []

    if task_title_query:
        tasks = Task.query.filter_by(title= task_title_query)
    else:
        tasks = Task.query.all()

    for task in tasks:
        task_response.append(
            task.to_dict()
        )
    
    return jsonify(task_response),200




