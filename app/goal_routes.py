
from app import db
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response,request, abort
from dotenv import load_dotenv
import os
from app.models.task import Task

load_dotenv()
goal_bp = Blueprint("goal", __name__,url_prefix="/goals")

#Helper function
def valid_int(number):
    try:
        return int(number)     
    except:
        abort(make_response({"error": f"{number} must be an int"}, 400))
#Helper function
def get_goal_from_id(goal_id):
    goal_id = valid_int(goal_id)
    goal = Goal.query.get(goal_id)
    if goal:
        return goal
    else:
        abort(make_response({"description": "Goal not found"}, 404))


@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details":"Invalid data"}, 400)
    
    new_goal = Goal(title=request_body["title"])
    
    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@goal_bp.route("", methods=["GET"])
def read_all_goals():
    goals = Goal.query.all()
    response = [goal.to_dict() for goal in goals]
    return jsonify(response)

@goal_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    response_goal = get_goal_from_id(goal_id)
    return {"goal":response_goal.to_dict()}

@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    response_goal = get_goal_from_id(goal_id)
    request_body = request.get_json()
    if "title" not in request_body:
        return "Incomplete data", 400
    response_goal.title = request_body["title"]

    db.session.commit()

    return {"goal":response_goal.to_dict()}

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    response_goal = get_goal_from_id(goal_id)
    
    db.session.delete(response_goal)
    db.session.commit()
    
    return {
        "details":f'Goal {response_goal.goal_id} "{response_goal.title}" successfully deleted'
    } 
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])  # to update tasks giving a specific goal
def update_tasks_with_specific_goal(goal_id): # this scenario is when there is already tasks defined without creating relationship with goal at first
     # the tasks were created in the db by the test, I am accessing these tasks,
    # and link them with their goal and commit back
    
    goal = get_goal_from_id(goal_id)
    request_body = request.get_json()   
    for ids in request_body["task_ids"]:
        task = Task.query.get(ids)
        goal.tasks.append(task)
        # task.goal = goal...this also works instead of line 79

        db.session.commit()
    
    return {
        "id":goal.goal_id,
        "task_ids":[task.task_id for task in goal.tasks]
    }
@goal_bp.route("/<goal_id>/tasks", methods=["GET"]) 
def read_tasks_with_specific_goal(goal_id):  
    goal = get_goal_from_id(goal_id)
    tasks_response = [task.to_dict() for task in goal.tasks]      
    
    return jsonify({
                "id": goal.goal_id,
                "title": goal.title,
                "tasks": tasks_response
    })