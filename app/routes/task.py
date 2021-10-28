from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_bp.route('', methods=['GET'])
def read_all_tasks():
    tasks = db.session.query(Task).filter(Task.accessible==True)
    response_body = [task.to_dict() for task in tasks]
    return make_response(jsonify(response_body), 200)

@task_bp.route('', methods=['POST'])
def create_new_task():
    request_body = request.get_json()
    task_to_create = Task(
        title=request_body['title'],
        description=request_body['description']
    )
    
    db.session.add(task_to_create)
    db.session.commit()

    return make_response(f'Task {task_to_create.title} added to task list', 201)

@task_bp.route('/<task_id>', methods=['GET'])
def read_single_task(task_id):
    task = Task.query.get(task_id)
    response_body = task.to_dict()
    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>', methods=['PUT'])
def update_single_task(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)
    if request_body['title']:
        task.title = request_body['title']
    if request_body['description']:
        task.description = request_body['description'] 
    
    db.session.commit()

    return make_response(f'Task id {task_id} updated', 200)

@task_bp.route('/<task_id>', methods=['DELETE'])
def delete_single_task(task_id):
    task = Task.query.get(task_id)
    task.accessible = False
    db.session.commit()
    return make_response(f'Task id {task_id} deleted', 200)
    