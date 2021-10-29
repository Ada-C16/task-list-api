from app import db
from flask import Blueprint, request, make_response, jsonify, abort
from app.models.task import Task

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
        return make_response({"details" : "Invalid data"}, 400)
    
    if request_body["completed_at"] == None:
        pass    
    
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"], 
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

        
    return make_response("201 CREATED", 201) 

#-----------------
#READ
@tasks_list_bp.route("", methods=["GET"])
def read_all_tasks():
    tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response)

@tasks_list_bp.route("/<id>", methods=["GET"])
def read_one_task(id):
    task = get_task_from_id(id)
    return make_response({"task" : task.to_dict()},200)
    


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
    
    return make_response({"task" : task.to_dict()},200)


#DELETE
@tasks_list_bp.route("/<id>", methods=["DELETE"]) 
def delete_task(id):
    task = get_task_from_id(id)
    
    db.session.delete(task)
    db.session.commit()
    
    return make_response({"details": f"Task {id} {task.description} successfully deleted"},200) 