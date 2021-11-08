from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_bp.route('', methods=['GET'])
def read_all_tasks():
    tasks = db.session.query(Task).filter(Task.accessible==True)
    
    if request.args.get('sort') == 'asc':
        tasks = tasks.order_by(Task.title.asc())
    elif request.args.get('sort') == 'desc':
        tasks = tasks.order_by(Task.title.desc())

    response_body = [task.to_dict() for task in tasks]
    return make_response(jsonify(response_body), 200)

@task_bp.route('', methods=['POST'])
def create_new_task():
    request_body = request.get_json()
    if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
        response_body = {
            'details': 'Invalid data'
        }
        return make_response(jsonify(response_body), 400)
    # goal = None if 'goal_id' not in request_body else request_body['goal_id']
    task_to_create = Task(
        title=request_body['title'],
        description=request_body['description'],
        completed_at=request_body['completed_at']
        # goal_id=
    )
    
    db.session.add(task_to_create)
    db.session.commit()

    response_body = {
        'task': task_to_create.to_dict()
    }

    return make_response(jsonify(response_body), 201)

@task_bp.route('/<task_id>', methods=['GET'])
def read_single_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
        
    response_body = {'task': task.to_dict()} if not task.goal_id else {'task': task.to_dict_with_goal()}
    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>', methods=['PUT'])
def update_single_task(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)

    if 'title' not in request_body or 'description' not in request_body:
        return make_response('Invalid data', 400)
        
    task.title = request_body['title']
    task.description = request_body['description'] 

    db.session.commit()

    response_body = {
        'task': Task.query.get(task_id).to_dict()
    }
    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>/mark_complete', methods=['PATCH'])
def update_single_task_complete(task_id):
    # request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
        
    task.completed_at = datetime.utcnow()
    db.session.commit()

    # "Someone just completed the task My Beautiful Task"
    slack_channel_id = os.environ.get('SLACK_CHANNEL_ID')
    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
    requests.post(
        'https://slack.com/api/chat.postMessage',
        headers={'Authorization': f'Bearer {slack_bot_token}'},
        data={
            'channel': slack_channel_id,
            'text': f'Someone just completed the task {task.title}'
        }
    )

    response_body = {
        'task': task.to_dict()
    }

    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>/mark_incomplete', methods=['PATCH'])
def update_single_task_incomplete(task_id):
    # request_body = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
        
    task.completed_at = None
    db.session.commit()

    response_body = {
        'task': task.to_dict()
    }

    return make_response(jsonify(response_body), 200)

@task_bp.route('/<task_id>', methods=['DELETE'])
# def delete_single_task(task_id):
#     task = Task.query.get(task_id)
#     if not task or not taks.accessible:
#         return make_response('', 404)
#     task.accessible = False
#     db.session.commit()
#     response_body = {
#         'details': f'Task {task_id} "{task.title}" successfully deleted'
#     }
#     return make_response(jsonify(response_body), 200)
def delete_single_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response('', 404)
    
    db.session.delete(task)
    db.session.commit()

    response_body = {
        "details": f'Task {task.id} "{task.title}" successfully deleted'
    }
    return make_response(jsonify(response_body), 200)