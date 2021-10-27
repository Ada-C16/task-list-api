from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request

task_bp = Blueprint("task", __name__, url_prefix="/tasks")

def helper_func_convert_a_task_to_dict(task):
    task_dict = {
        "id" : task.task_id,
        "title" : task.title,
        "description" : task.description,
        "is_complete" : True if task.completed_at else False
    }

    return task_dict


@task_bp.route("", methods=["GET", "POST"])
def handle_a_task():
    if request.method == "GET":
        all_tasks = Task.query.all()
        if not all_tasks:
            return jsonify([]), 200
        else:
            tasks_response = []
            for task in all_tasks:
                tasks_response.append(helper_func_convert_a_task_to_dict(task))
            return jsonify(tasks_response), 200

    elif request.method == "POST":
        request_body = request.get_json()

        try: 
            new_task = Task(title=request_body["title"],
                            description=request_body["description"],
                            completed_at=request_body["completed_at"])
            
            db.session.add(new_task)
            db.session.commit()

            helper_func_convert_a_task_to_dict(new_task)

            return {"task" : helper_func_convert_a_task_to_dict(new_task)}, 201
        except KeyError:
            return {
                "details": "Invalid data"
                }, 400


@task_bp.route("/<int:task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task_with_id(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "GET":
        if task:
            return {"task":helper_func_convert_a_task_to_dict(task)}, 200

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            task.title = request_body['title']
            task.description = request_body['description']

            db.session.add(task)
            db.session.commit()
            return {    
                "task" : helper_func_convert_a_task_to_dict(task)
                }, 200
        except KeyError:
            return {
                "message" : "require both title and description"
                }, 400
    
    else:   # Delete
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task.task_id} \"{task.title}\" successfully deleted'}
    
    






