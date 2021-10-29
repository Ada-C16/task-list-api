from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.goal import Goal
from app.models.task import Task

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
        return make_response(jsonify(response_body), 400)
    
    goal_to_create = Goal(
        title=request_body['title']
    )

    db.session.add(goal_to_create)
    db.session.commit()

    response_body = {
        'goal': goal_to_create.to_dict()
    }
    return make_response(jsonify(response_body), 201)

@goal_bp.route('/<goal_id>', methods=['GET'])
def get_single_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response('', 404)
        
    response_body = {'goal': goal.to_dict()}
    return make_response(jsonify(response_body), 200)

@goal_bp.route('/<goal_id>', methods=['PUT'])
def update_single_goal(goal_id):
    request_body = request.get_json()
    if 'title' not in request_body:
        response_body = {
            'details': 'Invalid data'
        }
        return make_response(jsonify(response_body), 400)

    goal = Goal.query.get(goal_id)
    goal.title = request_body['title']
    db.session.commit()
    response_body = {
        'goal': goal.to_dict()
    }
    return make_response(jsonify(response_body), 200)

@goal_bp.route('/<goal_id>', methods=['DELETE'])
def delete_single_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response('', 404)
    
    db.session.delete(goal)
    db.session.commit()

    response_body = {
        'details': f'Goal {goal_id} "{goal.title}" successfully deleted'
    }
    return make_response(jsonify(response_body), 200)

# @authors.route("/<author_id>/books", methods=["GET", "POST"])
# def handle_authors_books(author_id):
#     if request.method == "POST":
#         request_body = request.get_json()

#         # refer to the documentation and try
#         # completing this endpoint yourself

#         db.session.add(new_book)
#         db.session.commit()

#         return make_response(f"Book {new_book.title} by {new_book.author.name} successfully created", 201)

@goal_bp.route('/<goal_id>/tasks', methods=['POST'])
def post_task_ids_to_goal(goal_id):
    request_body = request.get_json()
    if 'task_ids' not in request_body:
        return make_response('Invalid data', 400)

    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response('', 404)

    for task_id in request_body['task_ids']:
        task = Task.query.get(task_id)
        if task not in goal.tasks:
            goal.tasks.append(task)
    db.session.commit()

    response_body = {
        'id': goal.id,
        'task_ids': [task.id for task in goal.tasks]
    }
    return make_response(jsonify(response_body), 200)
