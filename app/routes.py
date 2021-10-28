from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            error_dict = {"details": "Invalid data"}
            return jsonify(error_dict), 400
        
        
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"]
                        )
        
        db.session.add(new_task)
        db.session.commit()

        task_response = {"task": new_task.create_dict()}
        return jsonify(task_response), 201

    elif request.method == "GET":
        name_from_url = request.args.get("name")
        if name_from_url:
            tasks = Task.query.filter_by(name=name_from_url).all()
            if not tasks:
                tasks = Task.query.filter(Task.name.contains(name_from_url))
                
        else:
            tasks = Task.query.all()
            
        tasks_response = []
        for task in tasks:
            tasks_response.append(task.create_dict())
        
        if not tasks_response:
            tasks = Task.query.all()
            for task in tasks:
                tasks_response.append(task.create_dict())
        
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE", "PATCH"])
def task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404
    
    if request.method == "GET":
        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200
    
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.iscomplete = None

        db.session.commit()

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        
        delete_string = f'Task {task.task_id} "{task.title}" successfully deleted'
        delete_message = {"details": delete_string}
        
        return jsonify(delete_message), 200
        