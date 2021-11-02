from app import db
from flask import Blueprint, request, make_response, jsonify, abort
from app.models.task import Task
from datetime import datetime

# DEFINE BLUEPRINT
tasks_list_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

#-----------------
#HELPER FUNCTIONS 
def get_task_from_id(id):
    try:
        id = int(id)
    except:
        abort(400, {"error": "invalid id"})
    return Task.query.get_or_404(id)


#-----------------
#CREATE
@tasks_list_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(jsonify({"details" : "Invalid data"}), 400)
    
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

        
    return make_response(jsonify({"task": new_task.to_dict()}), 201)

#-----------------
#READ
@tasks_list_bp.route("", methods=["GET"])
def read_all_tasks():
    sort_query = request.args.get("sort")
    
    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    
    else: 
        tasks = Task.query.all()
    

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response)

@tasks_list_bp.route("/<id>", methods=["GET"])
def read_one_task(id):
    task = get_task_from_id(id)
    return make_response(jsonify({"task" : task.to_dict()}),200)
    

#-----------------
#UPDATE
@tasks_list_bp.route("/<id>", methods=["PUT"]) 
def update_task(id):
    task = get_task_from_id(id)
    request_body = request.get_json()
    
    #if "title" or "description" not in request body return 400
    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    
    
    db.session.commit()
    
    return make_response(jsonify({"task" : task.to_dict()}),200)

#-----------------
#UPDATE COMPLETION STATUS
@tasks_list_bp.route("/<id>/<completion_status>", methods=["PATCH"])
def mark_complete(id, completion_status):
    task = get_task_from_id(id)
    #task_dict = {}
    
    if completion_status == "mark_complete":
        task.completed_at = datetime.date
    if completion_status == "mark_incomplete":
        task.completed_at = None


    #task_dict["task"] = task.to_dict()
    return jsonify({"task" : task.to_dict()})
    

#-----------------
#DELETE
@tasks_list_bp.route("/<id>", methods=["DELETE"]) 
def delete_task(id):
    task = get_task_from_id(id)
    
    db.session.delete(task)
    db.session.commit()
    
    return make_response(jsonify({'details': f'Task {task.task_id} "{task.title}" successfully deleted'}),200) 

