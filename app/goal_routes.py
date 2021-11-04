from flask import Blueprint, jsonify, abort, request
from app import db
from app.models.goal import Goal
from app.models.task import Task
import requests
import os
from dotenv import load_dotenv 

load_dotenv()

goals_bp = Blueprint("goal", __name__, url_prefix="/goals")

def valid_id(model, id):
    try:
        id = int(id)
    except: 
        abort(400, {"error": "invalid id"})
    return model.query.get_or_404(id)

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals(): 
    request_body = request.get_json()

    if request.method == "POST": 
        if "title" not in request_body: 
            return jsonify({"details": "Invalid data"}), 400

        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        goals_dict = {}
        goals_dict["goal"] = new_goal.to_dict()
        return jsonify(goals_dict), 201
    
    if request.method == "GET":
        goals_response = []
        goals = Goal.query.all()
        for goal in goals: 
            goals_response.append(goal.to_dict())

        return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    goal_dict = {}
    goal = valid_id(Goal, goal_id)

    if request.method == "GET":
        goal_dict["goal"] = goal.to_dict()
        return jsonify(goal_dict), 200

    if request.method == "PUT": 
        request_body = request.get_json() 
        goal.title = request_body["title"]
        goal_dict["goal"] = goal.to_dict()
        db.session.commit()
        return jsonify(goal_dict), 200

    if request.method == "DELETE":
        if goal:
            db.session.delete(goal)
            db.session.commit()
            return jsonify({"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}), 200

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_tasks_realted_to_goal(goal_id):
    goal = valid_id(Goal, goal_id)
    
    if request.method == "POST":
        request_body = request.get_json()
        
        goal.tasks = [valid_id(Task, task_id) for task_id in request_body["task_ids"]]

        db.session.commit()

        return {"id": int(goal_id), "task_ids": request_body["task_ids"]}, 200

    if request.method == "GET": 
        goal = goal.to_dict()
        goal["tasks"] = [valid_id(Task, task_id) for task_id in goal.tasks]
        return goal, 200
