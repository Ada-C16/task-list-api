from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, abort

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET"])
def get_goals():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title).all()
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc()).all()
    else:
        goals = Goal.query.all()

    goals_response = [goal.to_dict() for goal in goals]
    return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify(None), 404

    response_body = goal.verbose_goal_dict()
    
    return jsonify(response_body), 200


@goals_bp.route("", methods=["POST"])
def post_new_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    response_body = {
        "goal": (new_goal.to_dict())
    }
    return jsonify(response_body), 201

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_new_tasks_for_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal_id == None:
        return jsonify(None), 404
        
    request_body = request.get_json()
    tasks = []
    for num in request_body["task_ids"]:
        task = Task.query.get(num)
        tasks.append(task)
    goal.tasks = tasks
    db.session.commit()

    response_body = goal.goal_with_tasks_dict()
    
    return jsonify(response_body), 200

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_single_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify(None), 404

    response_body = {
        "goal": (goal.to_dict())
    }
    return jsonify(response_body), 200

@goals_bp.route("/<goal_id>", methods=["PUT"])
def put_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(None), 404

    form_data = request.get_json()
    goal.title = form_data["title"]

    db.session.commit()

    response_body = {
        "goal": (goal.to_dict())
    }
    return jsonify(response_body), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(None), 404
    
    db.session.delete(goal)
    db.session.commit()
    return jsonify({
        'details': f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }), 200 
