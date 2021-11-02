from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from datetime import datetime
import requests
from app import SLACK_TOKEN

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('', methods=['GET', 'POST'])
def handle_tasks():
        if request.method == 'GET':
            sort_query = request.args.get("sort")
            if sort_query == 'asc':
                tasks = Task.query.order_by(Task.title.asc())
            elif sort_query == 'desc':
                tasks = Task.query.order_by(Task.title.desc())
            else:
                tasks = Task.query.all()
            tasks_list = []
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
            if 'title' not in request_body.keys() or 'description' not in request_body.keys() \
                                                  or 'completed_at' not in request_body.keys():
                return make_response({"details": "Invalid data"}, 400)
            else:
                new_task = Task(title=request_body['title'],
                                description=request_body['description'],
                                completed_at= datetime.utcnow()
                                )
                db.session.add(new_task)
                db.session.commit()
                return make_response({"task": { "id": new_task.task_id,
                                                "title": new_task.title,
                                                "description": new_task.description,
                                                "is_complete": False if new_task.completed_at is None else True
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
        task.completed_at = datetime.utcnow()
        
        db.session.commit()
        return make_response({"task": { "id": task.task_id,
                                        "title": task.title,
                                        "description": task.description,
                                        "is_complete": False if task.completed_at is None else True  
                                        }})
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"})

@tasks_bp.route('/<task_id>/mark_complete', methods=['PATCH'])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if task is None: 
        return jsonify(task), 404
    else: 
        task.completed_at = datetime.now()
        url = 'https://slack.com/api/chat.postMessage'
        channel_id = "C02J08B9S0N"
        data = {
                "channel": channel_id,
                "token": SLACK_TOKEN,
                "text": "Monica, is that you?? You hella forgot what you named your bot -_-"
               }
        r = requests.post(url, data=data)
        
    db.session.commit()
    return make_response({"task": {"id": task.task_id,
                                   "title": task.title,
                                   "description": task.description,
                                   "is_complete": True
                                  }})

@tasks_bp.route('/<task_id>/mark_incomplete', methods=['PATCH'])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify(task), 404
    else:
        task.completed_at = None
    db.session.commit()
    return make_response({"task": {"id": task.task_id,
                                   "title": task.title,
                                   "description": task.description,
                                   "is_complete": False
                                  }})

