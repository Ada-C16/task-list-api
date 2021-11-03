from app import db
from flask import Blueprint
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, make_response
import requests
import os
from dotenv import load_dotenv
from datetime import datetime


#********************* TASK routes ******************************

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
@tasks_bp.route("", methods=["GET", "POST"])
def handle_all_tasks():
  
  if request.method == "GET":
    sort_query = request.args.get("sort")
    if sort_query == None:
      tasks = Task.query.all()
    elif sort_query == "desc":
      tasks = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
      tasks = Task.query.order_by(Task.title.asc())
    else:
      tasks = Task.query.all()
            
    tasks_response = []
    for task in tasks:
      tasks_response.append({
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at is not None
        })
    return jsonify(tasks_response), 200
  
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
    
    return jsonify({"task": {
        "id": new_task.task_id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": new_task.completed_at is not None}}), 201
  
@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE", "PATCH"])
def handle_single_task(task_id):
  task = Task.query.get_or_404(task_id)

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
      
      return jsonify({"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}}), 200
      
  elif request.method == "DELETE":
      
    db.session.delete(task)
    db.session.commit()
    return jsonify(
      {"details": f'Task {task.task_id} "{task.title}" successfully deleted'})
  

#********************* Tasks Mark Complete, Mark Incomplete ******************************

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
  
  task = Task.query.get_or_404(task_id)
  task.completed_at = datetime.utcnow()
  db.session.commit()
  
  response_body = {"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}}
  
  path = "https://slack.com/api/chat.postMessage"
  header = {"Authorization: os.getenv(BOT_TOKEN)"}
  query_params = {
    "channel": "task-notification",
    "text": f"Someone completed the task {task.title}"}
  response = requests.post(path, params=query_params, headers=header)
    
  return jsonify(response_body), 200
  
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_completed_task_incomplete(task_id):
  task = Task.query.get_or_404(task_id)
  
  if request.method == "PATCH":
    task.completed_at = None
    
    db.session.commit()
    return jsonify({"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
          "is_complete": task.is_complete()}}), 200

# ********************* Goal routes ******************************

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST", "GET"])
def handle_all_goals():
  if request.method == "GET":
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
      goals_response.append({"id": goal.goal_id,
        "title": goal.title})
      
    return jsonify(goals_response), 200
  
  if request.method == "POST":
    request_body = request.get_json()
    
    if not request_body:
      return jsonify({"details": "Invalid data"}), 400
    else: 
      goal = Goal(title = request_body["title"])
    
      db.session.add(goal)
      db.session.commit()
      
      return make_response({"goal": {
          "id": goal.goal_id,
          "title": goal.title}}, 201)
  

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_goal(goal_id):
  goal = Goal.query.get_or_404(goal_id)

  if request.method == "GET":
    return {"goal": {
        "id": goal.goal_id,
        "title": goal.title}}, 200
  
  elif request.method == "PUT":
      request_body = request.get_json()
      goal.title=request_body["title"] 
  
      db.session.commit()
      
      return jsonify({"goal": {
        "id": goal.goal_id,
        "title": goal.title}}), 200
      
  elif request.method == "DELETE":
    db.session.delete(goal)
    db.session.commit()
    
    return jsonify(
      {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'})
    

#********************* Task / Goal routes ******************************

# GET 
@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_with_goal(goal_id):
  goal = Goal.query.get_or_404 (goal_id) 

  tasks_with_goals = Task.query.all() 
  tasks_with_goals_list = []
  
  for task in tasks_with_goals:
    tasks_with_goals_list.append({
      "id": task.task_id, 
      "goal_id": task.goal_id, 
      "title": task.title, 
      "description": task.description, 
      "is_complete": task.is_complete()})

  return {"id": goal.goal_id,
      "title": goal.title,
      "tasks": [{
        "id": task.task_id,
        "goal_id": task.goal_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete()}]}, 200
    

#POST
@goals_bp.route("/<goal_id>/tasks", methods=["POST"], strict_slashes=False)
def post_goals_with_tasks(goal_id):
    
  request_data = request.get_json()

  for task_id in request_data["task_ids"]:
    task = Task.query.get_or_404(task_id)
    task.goal_id = goal_id 
  db.session.commit()

  return jsonify({"id": (task.goal_id),"task_ids": request_data["task_ids"]}), 200

