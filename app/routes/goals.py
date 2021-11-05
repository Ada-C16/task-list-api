from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, abort

goal_bp =  Blueprint('goals', __name__, url_prefix= "/goals")


# POST create a new  goal
@goal_bp.route('', methods = ['POST'])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        response_body = {"details": "Invalid data. Title is required"} 
        return make_response(response_body, 400)
    try:
        new_goal = Goal(title=request_body["title"])
        # add new entity and commit it 
        db.session.add(new_goal)
        db.session.commit()

        response_body = {
            "goal": new_goal.to_dict()
        }
        return make_response(jsonify(response_body),201)  
    except:
        abort(422)

#GET read all goals 
@goal_bp.route('', methods = ['GET'])
def read_all_goals():
    goals = Goal.query.all()

    try:
        response_body = []
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

# DELETE one goal by id
@goal_bp.route('/<goal_id>', methods = ['DELETE'])
def delete_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    try:
        # delete entity and commit it
        db.session.delete(goal)
        db.session.commit()
        response_body ={"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}
        return make_response(response_body), 200
    except Exception:
        abort(422)

# UPDATE one goal by id
@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    try:
        request_body = request.get_json()
        if not request_body: 
            abort(400)
        elif "title" in request_body:
            goal.title = request_body["title"]
        # commit changes to db
        db.session.commit()
        response_body = {
            "goal": goal.to_dict()
        }
        return make_response(response_body, 200)
    except Exception: 
        abort(400)


''' -------- GOAL/TASK ONE-TO-MANY RELATIONSHIP --------'''


# POST
@goal_bp.route("/<goal_id>/tasks", methods= ['POST'])
def handle_tasks_goals(goal_id):
    # Becca, why is it a POST and not a PATCH method?
    goal = get_goal_by_id(goal_id)
    goal_id = goal.goal_id

    try:  
        request_body =  request.get_json()
        if not request_body:
            abort(400)         
        elif "task_ids" in request_body:
            task_ids = request_body["task_ids"]
            for item in task_ids:
                task = Task.query.get_or_404(item)
                task.goal_id = goal_id
                db.session.commit()

        response_body = {"id": goal_id,
                        "task_ids": [int(item) for item in task_ids]}        
        return make_response(response_body, 200)       
    except Exception:
        abort(422)


@goal_bp.route("/<goal_id>/tasks", methods= ['GET'])
def read_tasks_goals(goal_id):
    goal = get_goal_by_id(goal_id)
    
    try:
        tasks_list = []
        tasks = Task.query.filter_by(goal_id=goal_id).all()
        for task in tasks:
            tasks_list.append(task.to_dict_goal_task())     

        response_body = {"id": goal.goal_id, 
                        "title": goal.title,
                        "tasks": tasks_list}
        return make_response(jsonify(response_body)), 200    
    except Exception:
        abort(422)



'''------  Error Handling - Handles 402/400/422 errors ------- '''

@goal_bp.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not found"}),404

@goal_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "Bad request"}),400

@goal_bp.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}),422



''' --------- Helper functions ---------'''

def get_goal_by_id(goal_id):
    valid_int(goal_id, "goal_id")
    return Goal.query.get_or_404(goal_id, description='{Goal not found}')

def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f'{parameter_type} must be an integer'}, 400))
