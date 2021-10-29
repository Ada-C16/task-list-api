from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('', methods=['GET', 'POST'])
def handle_tasks():
        if request.method == 'GET':
            tasks_list = []
            tasks = Task.query.all()
            for task in tasks:
                tasks_list.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at is None else task.completed_at
                })
            return jsonify(tasks_list)
            
        elif request.method == 'POST':
            request_body = request.get_json()
            new_task = Task(title=request_body['title'],
                            description=request_body['description'],
                            completed_at=request_body['completed_at']
                            )
            db.session.add(new_task)
            db.session.commit()
            return make_response({"task": { "id": new_task.task_id,
                                            "title": new_task.title,
                                            "description": new_task.description,
                                            "is_complete": False if new_task.completed_at is None else new_task.completed_at  
                                            }}, 201)

@tasks_bp.route('/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404
    elif request.method == 'GET':
        return {"task": { "id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": False if task.completed_at is None else task.completed_at  
                        }}
    elif request.method == 'PUT':
        updates = request.get_json()
        task.title = updates['title']
        task.description = updates['description']
        
        db.session.commit()
        return make_response({"task": { "id": task.task_id,
                                        "title": task.title,
                                        "description": task.description,
                                        "is_complete": False if task.completed_at is None else task.completed_at  
                                        }})
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"})