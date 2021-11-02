from app import db
from app.models.goal import Goal
from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, abort



goal_bp =  Blueprint('goals', __name__, url_prefix= "/goals")



# POST- create a new  goal
@goal_bp.route('', methods = ['POST'])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        response_body = {"details": "Invalid data"} 
        return make_response(response_body, 400)

    try:
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        response_body = {
            "goal": new_goal.to_dict()
        }

        return make_response(jsonify(response_body),201)
    
    except:
        abort(422)



#GET - read all goals 
@goal_bp.route('', methods = ['GET'])
def read_all_goals():
    goals = Goal.query.all()
    response_body = []
    try:
        for goal in goals:
            response_body.append(goal.to_dict())     
        return  make_response(jsonify(response_body), 200)
    
    except:
        abort(400)

# GET one goal by id
@goal_bp.route('/<goal_id>', methods = ['GET'])
def read_one_goal(goal_id):
    goal = get_goal_by_id(goal_id)

    try:
        response_body = {"goal": goal.to_dict()}
        return make_response(jsonify(response_body)), 200

    except Exception: 
        abort(400)


@goal_bp.route('/<goal_id>', methods = ['DELETE'])
def delete_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    try:
        db.session.delete(goal)
        db.session.commit()
        response_body ={"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}

        return make_response(response_body), 200

    except Exception:
        abort(422)

@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_by_id(goal_id)

    try:
        request_body = request.get_json()
        if not request_body: 
            abort(400)

        if "title" in request_body:
            goal.title = request_body["title"]
        
        db.session.commit()

        response_body = {
            "goal": goal.to_dict()
        }
        return make_response(response_body, 200)

    except Exception: 
        abort(400)







'''Error Handling - Handles 402/400/422 errors'''

@goal_bp.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not found"}),404

@goal_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "Bad request"}),400

@goal_bp.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}),422




''' Helper functions '''

def get_goal_by_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description='{Goal not found}')


def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f'{parameter_type} must be an integer'}, 400))
