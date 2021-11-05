from flask import Blueprint, jsonify, abort, request
from app import db
from app.models.goal import Goal
from app.models.task import Task
from dotenv import load_dotenv 

load_dotenv()

goals_bp = Blueprint("goal", __name__, url_prefix="/goals")

def valid_id(model, id):
    """If ID is an int, returns the model object with that ID.
        If ID is not an int, returns 400.
        If model object with that ID doesn't exist, returns 404."""
    try:
        id = int(id)
    except: 
        abort(400, {"error": "invalid id"})
    return model.query.get_or_404(id)

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals(): 
    """Handles post and get requests for /goals"""
    request_body = request.get_json()

    if request.method == "POST": 
        if "title" not in request_body: 
            return {"details": "Invalid data"}, 400

        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        goals_dict = {}
        goals_dict["goal"] = new_goal.to_dict()
        return goals_dict, 201
    
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = [goal.to_dict() for goal in goals]

        return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_goal(goal_id):
    """Handles get, put, and delete requests for one goal \
        with a given id at goals/<goal_id>"""
    goal_dict = {}
    goal = valid_id(Goal, goal_id)

    if request.method == "GET":
        goal_dict["goal"] = goal.to_dict()
        return goal_dict, 200

    if request.method == "PUT": 
        request_body = request.get_json() 
        goal.title = request_body["title"]
        goal_dict["goal"] = goal.to_dict()
        db.session.commit()
        return goal_dict, 200

    if request.method == "DELETE":
        if goal:
            db.session.delete(goal)
            db.session.commit()
            return {"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}, 200

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_tasks_realted_to_goal(goal_id):
    """Handles post and get requets for a goal with a given ID \
        and all tasks related to it at /goals/<goal_id>/tasks"""
    goal = valid_id(Goal, goal_id)
    
    if request.method == "POST":
        request_body = request.get_json()
        goal.tasks = [valid_id(Task, task_id) for task_id in request_body["task_ids"]]

        db.session.commit()

        return {"id": int(goal_id), "task_ids": request_body["task_ids"]}, 200

    if request.method == "GET": 
        goal_dict = goal.to_dict()
        goal_dict["tasks"] = [valid_id(Task, task.task_id).to_dict() for task in goal.tasks]

        return goal_dict, 200
