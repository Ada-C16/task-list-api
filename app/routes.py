from re import L
from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task
from app import db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'GET':
        tasks = Task.query.all()
        # if not tasks:
        #     return make_response(jsonify({'message': 'No tasks found'}), 404)
        return jsonify([task.to_dict() for task in tasks]), 200

    elif request.method == 'POST':
        request_body = request.get_json()
        if isinstance(request_body, list):
            for task in request_body:
                new_task = Task(
                    title=task['title'],
                    description=task['description']
                    # priority=task['priority'],
                    # due_date=task['due_date']
                )
                db.session.add(new_task)
                return jsonify(task.to_dict() for task in request_body), 201
        else:
            new_task = Task(
                title=request_body['title'],
                description=request_body['description']
                # priority=request_body['priority'],
                # due_date=request_body['due_date']
            )
            db.session.add(new_task)
            db.session.commit()
            return jsonify(new_task.to_dict()), 201

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(jsonify({'message': 'Task not found'}), 404)
    return jsonify(task.to_dict()), 200