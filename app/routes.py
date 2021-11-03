from flask import Blueprint, jsonify, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import desc, asc
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
load_dotenv()

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")


@task_bp.route("", methods=["POST"])
def handle_tasks():
    """This endpoint takes in a json object and creates a new Task instance"""
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body\
            or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task": new_task.task_dict()}), 201


@task_bp.route("", methods=["GET"])
def get_tasks():
    """ This endpoint takes in a GET request and possibly a sorting query and returns 
    a sorted list of task instances or a non-sorted list of task instances """
    sort_query = request.args.get("sort")
    if sort_query == "desc":
        tasks = Task.query.order_by(desc("title"))
        task_list = [task.task_dict() for task in tasks]
    elif sort_query == "asc":
        tasks = Task.query.order_by(asc("title"))
        task_list = [task.task_dict() for task in tasks]
    else:
        tasks = Task.query.all()
        task_list = [task.task_dict() for task in tasks]
    return jsonify(task_list), 200


@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    """ This endpoint uses GET http method to find and return one specific instance of Task class """
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    if one_task.goal_id:
        return jsonify({"task": one_task.task_dict_with_goal()})
    return jsonify({"task": one_task.task_dict()}), 200


@task_bp.route("/<task_id>", methods=["PUT"])
def put_one_task(task_id):
    """ Edits the title and description information for a specific Task instance """
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    request_body = request.get_json()
    one_task.title = request_body["title"]
    one_task.description = request_body["description"]
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    """ Deletes a specific task instance based on the provided task id """
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    db.session.delete(one_task)
    db.session.commit()
    response_body = f'Task {task_id} "{one_task.title}" successfully deleted'
    return jsonify({"details": response_body}), 200


@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete_task(task_id):
    """ Takes one specific task and adds datetime completion stamp to database for this task instance """
    path = "https://slack.com/api/chat.postMessage"
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    one_task.completed_at = datetime.now(tz=None)
    requests.post(path, headers={"Authorization": os.getenv('BOT_TOKEN')},
                  data={"channel": "slack-api-test-channel",
                        "text": f"Someone just completed the task {one_task.title}"})
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete_task(task_id):
    """ Takes one specific task and adds datetime completion stamp to database for this task instance """
    one_task = Task.query.get(task_id)
    if one_task is None:
        return jsonify(one_task), 404
    one_task.completed_at = None
    db.session.commit()
    return jsonify({"task": one_task.task_dict()}), 200


@goal_bp.route("", methods=["POST"])
def post_goal():
    """ Creates new instance of Goal class """
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_goal = Goal(
        title=request_body["title"]
    )
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({"goal": new_goal.goal_dict()}), 201


@goal_bp.route("", methods=["GET"])
def get_goal():
    """ Uses http GET method to access all goal instances in database """
    goals = Goal.query.all()
    goals_response = [goal.goal_dict() for goal in goals]
    return jsonify(goals_response), 200


@goal_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    """ Uses http GET method to access one specific instance of goal class based on goal id """
    one_goal = Goal.query.get(goal_id)
    if one_goal is None:
        return jsonify(one_goal), 404
    return jsonify({"goal": one_goal.goal_dict()}), 200


@goal_bp.route("/<goal_id>", methods=["PUT"])
def put_one_goal(goal_id):
    """ Uses http method PUT to edit information in specific instance of goal class """
    one_goal = Goal.query.get(goal_id)
    if one_goal is None:
        return jsonify(one_goal), 404
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    one_goal.title = request_body["title"]
    db.session.commit()
    return jsonify({"goal": one_goal.goal_dict()}), 200


@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_one_goal(goal_id):
    """ Uses http DELETE method to allow user to delete specific instance of goal class """
    one_goal = Goal.query.get(goal_id)
    if one_goal is None:
        return jsonify(one_goal), 404
    db.session.delete(one_goal)
    db.session.commit()
    return jsonify({"details": f"Goal {one_goal.goal_id} \"{one_goal.title}\" successfully deleted"})


@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_goal_tasks(goal_id):
    """ Uses http POST method to add multiple task instances to one specific goal instance """
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(goal), 404
    request_body = request.get_json()
    for num in request_body["task_ids"]:
        task = Task.query.get(num)
        task.goal_id = goal_id
        goal.tasks.append(task)
    db.session.commit()
    return jsonify({"id": goal.goal_id, "task_ids":
                    [task["id"] for task in goal.goal_task_dict()["tasks"]]}), 200


@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    """ Uses http method GET to access all task instances attached to one specific goal instance """
    goal = Goal.query.get(goal_id)
    if goal is None:
        return jsonify(goal), 404
    return jsonify(goal.goal_task_dict()), 200
