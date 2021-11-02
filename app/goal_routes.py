
from app import db
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response,request, abort
from dotenv import load_dotenv
import os

load_dotenv()
goal_bp = Blueprint("goal", __name__,url_prefix="/goals")

@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"error":"Incomplete data"}, 400)
    
    new_goal = Goal(title=request_body["title"])
    
    db.session.add(new_goal)
    db.session.commit()

    return {
        "goal": new_goal.to_dict()
    }

@goal_bp.route("", methods=["GET"])
def read_all_goals():
    goals = Goal.query.all()
    response = [goal.to_dict() for goal in goals]
    return jsonify(response)
