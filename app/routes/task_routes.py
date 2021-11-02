from app.models.task import Task
from flask import jsonify
from flask import Blueprint, make_response, request
from app import db

task_bp = Blueprint("task", __name__,url_prefix="/tasks")
# get all tasks
@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
    #write query to fetch all tasks 
        tasks = Task.query.all()
        tasks_response = [task.to_dict() for task in tasks]
        return jsonify(tasks_response), 200
    
    elif request.method == "POST":
        request_body = request.get_json()
        if not "title" in request_body or not "description" in request_body or not "completed_at" in request_body:
            return jsonify({"details":"Invalid data"}), 400
        new_task = Task(title=request_body["title"], 
                        description=request_body["description"],
                        completed_at=request_body["completed_at"],
            
        )
        
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"task": new_task.to_dict()}), 201 
        
        

@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task_id = int(task_id)
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)
    if request.method == "GET":
    
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
            
        task.title = request_body["title"]
        task.description = request_body["description"]
            
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200
    
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details":f'Task {task.task_id} "{task.title}" successfully deleted'}), 200


# @task_bp.route("/<task_id>", methods=["GET"])
# def handle_task(task_id):
#     task_id = int(task_id)
#     task = Task.query.get(task_id)
#     if not task:
#         return make_response(f"Task {task_id} Bad data", 400)
    
    # if request.method == GET

    # for task in tasks:
    #     if task.id == task_id:
    #         return vars(task)

    # return "Not found", 404
