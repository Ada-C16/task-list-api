from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.goal import Goal

goal_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goal_bp.route('', methods=['GET'])
def get_all_goals():
    goals = Goal.query.all()
    response_body = [goal.to_dict() for goal in goals]

    return make_response(jsonify(response_body), 200)

@goal_bp.route('', methods=['POST'])
def create_new_goal():
    request_body = request.get_json()
    if 'title' not in request_body:
        response_body = {
            'details': 'Invalid data'
        }
        make_response(jsonify(response_body), 400)
    
    goal_to_create = Goal(
        title=request_body['title']
    )

    db.session.add(goal_to_create)
    db.session.commit()

    new_goal = db.session.query(Goal).filter(Goal.title==goal_to_create.title).one()
    response_body = {
        'goal': new_goal.to_dict()
    }
    return make_response(jsonify(response_body), 201)

@goal_bp.route('/<goal_id>', methods=['GET'])
def get_single_goals(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response('', 404)
        
    response_body = {'goal': goal.to_dict()}
    return make_response(jsonify(response_body), 200)