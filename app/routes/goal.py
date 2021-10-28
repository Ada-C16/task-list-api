from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.goal import Goal

goal_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goal_bp.route('', methods=['GET'])
def get_all_goals():
    goals = Goal.query.all()
    response_body = list()

    for goal in goals:
        response_body.append(goal.to_dict())

    return make_response(jsonify(response_body), 200)

# @goal_bp.route()