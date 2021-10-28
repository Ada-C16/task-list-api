from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            # if not task.completed_at:
            #     is_complete = False
            # else:
            #     is_complete = True
                
            tasks_response.append({
                "id" : task.id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : bool(task.completed_at)
            })

        return jsonify(tasks_response)

@tasks_bp.route("/<id>", methods=["GET", "PUT", "DELETE"])
def handle_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify(""), 201
    
    if request.method == "GET":
        return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }
    }

    
    # elif request.method == "POST":
    #     request_body = request.get_json()
    #     new_task = Task(title=request_body["title"], 
    #     description=request_body["description"], completed_at=request_body["completed_at"])

    #     db.session.add(new_task)
    #     db.session.commit()
        
    #     if request_body["completed_at"]:
    #         is_complete = True
    #     else: 
    #         is_complete = False
        
    #     return jsonify("succesfully added"), 201

#POST /tasks
    #create a task where completed @ == None
    #ERROR: task with missing 'title' field
    #ERROR: task with missing 'description' field
    #create a task must contain completed @ (?????)

# @tasks_bp.route("/<id>", methods=["GET", "PUT", "DELETE"])
# def handle_tasks(id):
#     task = Task.query.get(id)
#     if task is None:
#         return jsonify(""), 201
    
#     if request.method == "GET":
#         if not task.completed_at:
#                 is_complete = False
#         else:
#                 is_complete = True
#         return {
#                 "id" : task.id,
#                 "title" : task.title,
#                 "description" : task.description,
#                 "is_complete" : is_complete
#         }

#GET /tasks/1
    #get existing taks
    #get a non-exisiting task

#PUT /tasks/1
    #update task 
    #update task not found

#DELETE /tasks/1
    #delete task
    #delete task not found



