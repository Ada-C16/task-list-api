from flask import Blueprint, blueprints, jsonify, make_response, request 
from app import db
from app.models.goal import Goal
from datetime import datetime
import requests
import os
from dotenv import load_dotenv 

load_dotenv()

goals_bp = Blueprint("goal", __name__, url_prefix="/goals")

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
    goal_id = int(goal_id)
    goal = Goal.query.get_or_404(goal_id)
    goal_dict = {}

    if request.method == "GET":
        goal_dict["goal"] = goal.to_dict()
        return jsonify(goal_dict), 200

    if request.method == "PUT": 
        input_data = request.get_json() 
        goal.title = input_data["title"]
        goal_dict["goal"] = goal.to_dict()
        db.session.commit()
        return jsonify(goal_dict), 200

    if request.method == "DELETE":
        if goal:
            db.session.delete(goal)
            db.session.commit()
            return jsonify({"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}), 200