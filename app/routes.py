from app import db
from app.models.task import Task
from flask import Blueprint, jsonify,request, make_response, abort
from datetime import date

tasks_bp = Blueprint("tasks",__name__,url_prefix="/tasks")
def valid_int(number,parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error":f"{parameter_type} must be an int"}, 400))
        
@tasks_bp.route("",methods=["GET"])
def handle_tasks():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response =[]
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response),200

@tasks_bp.route("/<task_id>",methods=["GET","put","DELETE"])
def get_task(task_id):
    valid_int(task_id, "task_id")
    task = Task.query.get_or_404(task_id)
    
    if request.method == "GET":
        return jsonify({"task":task.to_dict()}),200
    elif request.method == "PUT":
        request_body = request.get_json()
        if "title" in request_body:
            task.title = request_body["title"],
        if "description" in request_body:
            task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = request_body["completed_at"]
        db.session.commit()
        return jsonify({"task":task.to_dict()}),200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details":f'Task {task_id} "{task.title}" successfully deleted'}),200

@tasks_bp.route("",methods=["POST"])
def create_task():
    request_body = request.get_json()
    if 'title' not in request_body or 'description' not in request_body or\
    'completed_at' not in request_body:
        return jsonify({'details': "Invalid data"}),400
    
    new_task = Task(
        title=request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task":new_task.to_dict()}),201
    

    
