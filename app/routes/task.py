from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_bp.route('', methods=['GET'])
def read_all_tasks():
    tasks = db.session.query(Task).filter(Task.accessible==True)
    
    if request.args.get('sort') == 'asc':
        tasks = tasks.order_by(Task.title.asc())
    elif request.args.get('sort') == 'dsc':
        tasks = tasks.order_by(Task.title.dsc())

    response_body = [task.to_dict() for task in tasks]
    return make_response(jsonify(response_body), 200)

@task_bp.route('', methods=['POST'])
def create_new_task():
    request_body = request.get_json()
    if not request_body['title'] or not request_body['description'] or not request_body['completed_at']:
        response_body = {
            'details': 'Invalid data'
        }
        return make_response(jsonify(response_body), 400)

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
    if not task:
        return make_response('', 404)
        
    response_body = task.to_dict()
    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>', methods=['PUT'])
def update_single_task(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)

    if not request_body['title'] or not request_body['description']:
        return make_response('Invalid data', 400)
        
    task.title = request_body['title']
    task.description = request_body['description'] 

    db.session.commit()

    return make_response(f'Task id {task_id} updated', 200)

@task_bp.route('/<task_id>/mark_complete', methods=['PATCH'])
def update_single_task_complete(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
        
    task.completed_at = datetime.utcnow()
    db.session.commit()

    return make_response(jsonify(task.to_dict()), 200)

@task_bp.route('/<task_id>/mark_incomplete', methods=['PATCH'])
def update_single_task_incomplete(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
        
    task.completed_at = None
    db.session.commit()

    return make_response(jsonify(task.to_dict()), 200)

@task_bp.route('/<task_id>', methods=['DELETE'])
def delete_single_task(task_id):
    task = Task.query.get(task_id)
    if not task or not taks.accessible:
        return make_response('', 404)
    task.accessible = False
    db.session.commit()
    response_body = {
        'details': f'Task {task_id} "{task.title}" successfully deleted'
    }
    return make_response(jsonify(response_body), 200)
    