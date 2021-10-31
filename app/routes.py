from app import db
from flask import Blueprint
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, make_response


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_all_tasks():
  if request.method == "POST":
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
      return jsonify({"details": "Invalid data"}), 400
    
    new_task = Task(
      title=request_body["title"], 
      description=request_body["description"],
      completed_at=request_body["completed_at"])
                  
    db.session.add(new_task)
    db.session.commit()
    
    return new_task.to_json(), 200
  
  elif request.method == "GET":
    
    if not request.args:
      tasks = Task.query.all()
    
    else:
      title_query = request.args.get("title")
      sort_query = request.args.get("sort")
      if sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
      elif sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
            
    tasks_response = []
    for task in tasks:
      tasks_response.append(
       {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()
        })
    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_task(task_id):
  task = Task.query.get(task_id)
  
  if task is None:
    return "", 404

  if request.method == "GET":
    return {"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}}, 200
  
  elif request.method == "PUT":
      request_body = request.get_json()
  
      task.title=request_body["title"] 
      task.description=request_body["description"]
  
      db.session.commit()
      
      return {"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}}, 200
      
  elif request.method == "DELETE":
      
    db.session.delete(task)
    db.session.commit()
    return jsonify(
      {"details": f'Task {task.task_id} "{task.title}" successfully deleted'})




# Goal

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST", "GET"])
def handle_all_goals():
  if request.method == "POST":
    request_body = request.get_json()
    
    if "title" not in request_body:
      return jsonify({"details": "Invalid data"}), 400
    
    new_goal = Goal(title=request_body["title"])
                  
    db.session.add(new_goal)
    db.session.commit()
    
    return { "id": goal.goal_id,
        "title": goal.title}, 200
  
  elif request.method == "GET":
    goals = Goal.query.all()
    goals_response = []
    for goals in goals:
      goals_response.append(
       {
        "id": goal.goal_id,
        "title": goal.title})
    return jsonify(goals_response)

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_goals(goal_id):
  goal = Goal.query.get(goal_id)
  
  if goal is None:
    return "", 404

  if request.method == "GET":
    return {
        "id": goal.goal_id,
        "title": goal.title}, 200
  
  elif request.method == "PUT":
      request_body = request.get_json()
      goal.title=request_body["title"] 
  
      db.session.commit()
      
      return {
        "id": goal.goal_id,
        "title": goal.title}, 200
      
  elif request.method == "DELETE":
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})