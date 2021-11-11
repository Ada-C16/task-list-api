from app.models.goal import Goal
from flask import jsonify
from flask import Blueprint, make_response, request, jsonify, abort
from app import db
from app.models.task import Task


#helper functions
goal_bp = Blueprint("goal", __name__,url_prefix="/goals")
def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"})), 400

def get_goal_from_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description="{goal not found}")
# get all goal

@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goal = goal.to_dict()
            goals_response.append(goal)
        return jsonify(goals_response), 200 
        
    #write query to fetch all goals 
    
    
    elif request.method == "POST":
        request_body = request.get_json()
        if not "title" in request_body:
            return jsonify({"details":"Invalid data"}), 400
        new_goal = Goal(title=request_body["title"])
        
        db.session.add(new_goal)
        db.session.commit()
        return jsonify({"goal": new_goal.to_dict()}), 201 
        
        

@goal_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal_id = int(goal_id)
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    if request.method == "GET":
    
        return jsonify({"goal": goal.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
            
        goal.title = request_body["title"]
            
        db.session.commit()
        return jsonify({"goal": goal.to_dict()}), 200
    
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"details":f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}), 200
    
###WAVE 6 routes###
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def create_one_to_many(goal_id):
    request_body = request.get_json()
    goal = Goal.query.get(goal_id)
    task_ids = request_body["task_ids"]
    for task_id in task_ids:
        task=Task.query.get(task_id)
        goal.tasks.append(task) #list of task objects
        
    db.session.commit()
    return jsonify({"id": goal.goal_id,
                "task_ids":[task.task_id for task in goal.tasks]}), 200
    
@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_task_for_goal(goal_id):
    # request_body = request.get_json()
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    
    db.session.commit()    
    return jsonify({
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": [task.to_dict() for task in goal.tasks]
        }), 200