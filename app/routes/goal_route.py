from flask import Blueprint, make_response, request, jsonify
from app.models.goal import Goal
from app import db

# Blueprint
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# Helper functions
def get_goal_with_goal_id(goal_id):
    return Goal.query.get_or_404(goal_id, description={"details": "Invalid data"})


# Routes
@goal_bp.route("", methods = ["GET"])
def get_all_goals():
    """Read all goals"""

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()

    goal_response = []
    for goal in goals:
        goal_response.append(goal.to_dict())
    
    return jsonify(goal_response), 200


@goal_bp.route("", methods = ["POST"])
def add_goals():
    """Add goal to database"""

    request_body = request.get_json()
    if request_body is None:
        return make_response({"details": "Invalid data"}, 400)

    if "title" not in request_body or "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal": new_goal.to_dict()}), 201


@goal_bp.route("/<goal_id>", methods = ["GET"])
def read_one_goal(goal_id):
    goal = get_goal_with_goal_id(goal_id)
    return jsonify({"goal": goal.to_dict()})


@goal_bp.route("/<goal_id>", methods = ["PUT"])
def update_all_goal_info(goal_id):
    goal = get_goal_with_goal_id(goal_id)
    request_body = request.get_json()

    if request_body is None:
        return make_response({"details": "Invalid data"}, 400)

    if "id" in request_body:
        goal.id = request_body["id"]

    goal.title = request_body["title"]
    
    db.session.commit()

    return make_response({"goal": goal.to_dict()}, 200)


@goal_bp.route("/<goal_id>", methods = ["PATCH"])
def update_some_goal_info(goal_id):
    request_body = request.get_json()
    goal = get_goal_with_goal_id(goal_id)

    if "id" in request_body:
        goal.id = request_body["id"]
    if "title" in request_body:
        goal.title = request_body["title"]

    db.session.commit()
    return make_response({"goal": goal.to_dict()}, 200)


@goal_bp.route("/<goal_id>", methods = ["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_with_goal_id(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return jsonify({'details': f'Goal {goal.id} "{goal.title}" successfully deleted'})


@goal_bp.route("/<goal_id>/tasks", methods = ["POST"])
def post_task_to_goal(goal_id):
    goal = get_goal_with_goal_id(goal_id)
    request_body = request.get_json()

    