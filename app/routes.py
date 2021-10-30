from app import db
from flask import Blueprint
from app.models.task import Task
from flask import Blueprint, jsonify, request, make_response


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_all_tasks():
  if request.method == "POST":
    request_body = request.get_json()
    
    new_task = Task(
      title=request_body["title"], description=request_body["description"],completed_at=request_body["completed_at"])
                  
  
    db.session.add(new_task)
    db.session.commit()
    
    return new_task.to_json(), 200
  
  elif request.method == "GET":
    tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
      tasks_response.append(
       {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()
        })
    return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_task(task_id):
  task = Task.query.get(task_id)

  if request.method == "GET":
    return {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}, 200
  
  elif request.method == "PUT":
      request_body = request.get_json()
  
      task.title=request_body["title"] 
      task.description=request_body["description"]
      task.completed_at=request_body["completed_at"]

      db.session.commit()
      
      return {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}, 200
      
  elif request.method == "DELETE":
      
    db.session.delete(task)
    db.session.commit()
    return jsonify(
      {"details": f'Task {task.task_id} "{task.title}" successfully deleted'})



























# @tasks_bp.route("", methods=["GET"])
# def handle_all_tasks_get():
#     tasks = Task.query_all()
#     tasks_response = []
#     for task in tasks:
#       tasks_response.append({
#         "id": task.task_id,
#         "title": task.title,
#         "description": task.description,
#         "completed date": task.completed_at
#       })
#     return {
#         "id": task.task_id,
#         "title": task.title,
#         "description": task.description,
#         "is_complete": task.is_complete()
#       }

# @tasks_bp.route("", methods=["POST"])
# def handle_tasks_post():
#   request_body = request.get_json()
#   task = Task(
#     title = request_body["title"], description = request_body["description"],
#     completed_at = request_body["completed date"])
  
#   db.session.add(task)
#   db.session.commit()
  
#   return {
#         "id": task.task_id,
#         "title": task.title,
#         "description": task.description,
#         "is_complete": task.is_complete()
#       }, 201 
      


# @tasks_bp.route("/<task_id>", methods=["GET"])
# def handle_one_task_get(task_id):
#   task = Task.query.get(task_id)
#   if task is None:
#     return 404
  