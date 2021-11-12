from flask import Blueprint, jsonify, request
from app import db
from app.helpers import require_valid_goal_id, require_valid_goal_request_body, list_of_tasks
from app.models.task import Task
from app.models.goal import Goal

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# POST /goals Create a goal and commit to the db.
@goals_bp.route("", methods = ["POST"])
@require_valid_goal_request_body
def post_new_goal(request_body):

    new_goal = Goal(title = request_body["title"])
    db.session.add(new_goal)
    db.session.commit()

    return new_goal.create_goal_response(), 201

# GET /goals Get a list of all goals. 
@goals_bp.route("", methods = ["GET"])
def get_goals():
    goals = Goal.query.all()

    response_body = [goal.goal_body() for goal in goals]
    return jsonify(response_body), 200

# GET /goals/<goal_id> Get a specific goal.
@goals_bp.route("/<goal_id>", methods = ["GET"])
@require_valid_goal_id
def get_one_goal(goal):

    return goal.create_goal_response(), 200

# PUT /goals/<goal_id> Update a specific goal in the db and return the updated goal body.
@goals_bp.route("/<goal_id>", methods = ["PUT"])
@require_valid_goal_id
@require_valid_goal_request_body
def update_one_goal(goal, request_body):

    goal.title = request_body["title"]
    db.session.commit()

    return goal.create_goal_response(), 200

# DELETE /goals/<goal_id>  Delete a specific goal and return details of deletion.
@goals_bp.route("/<goal_id>", methods = ["DELETE"])
@require_valid_goal_id
def delete_one_goal(goal):

    db.session.delete(goal)
    db.session.commit()

    response_body = {"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}
    return response_body, 200 

# POST /goals/<goal_id>/tasks Assign tasks to a specific goal and return the goal body.
@goals_bp.route("/<goal_id>/tasks", methods = ["POST"])
@require_valid_goal_id
def assign_goal_to_task(goal):

    request_body = request.get_json()

    if "task_ids" not in request_body:
        return {"details": "Invalid data"}, 400

    task_ids = request_body["task_ids"]
    
    for task_id in task_ids:
        task = Task.query.get(task_id)
        task.goal_id = goal.goal_id

    db.session.commit()
    response_body = dict(id=goal.goal_id, task_ids=task_ids)
    return jsonify(response_body), 200

# GET /goals/<goal_id>/tasks Get a list of tasks assigned to a specific goal.
@goals_bp.route("/<goal_id>/tasks", methods = ["GET"])
@require_valid_goal_id
def get_tasks_for_specific_goal(goal):

    tasks = goal.tasks
    tasks_list = list_of_tasks(tasks)
    response_body = dict(id=goal.goal_id, title=goal.title, tasks=tasks_list)
    return jsonify(response_body), 200