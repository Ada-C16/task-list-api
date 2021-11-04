from flask import Blueprint, jsonify, request
from app.models.task import Task
from app.models.goal import Goal
from app import db
import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")
home_bp = Blueprint("home_bp", __name__, url_prefix="/")


#
# Start Tasks Routes
#


@home_bp.route("", methods=["GET"])
def home_page():
    if request.method == "GET":
        welcome = {"project": "task list",
                   "student": "kaitlyn",
                   "class": "spruce"}
        return jsonify(welcome), 200


@tasks_bp.route("", methods=["GET"])
def get_tasks():
    title_from_url = request.args.get("title")
    tasks = Task.task_arguments(title_from_url)

    tasks_response = []
    tasks_response = [task.create_dict() for task in tasks]

    if not tasks_response:
        tasks = Task.query.all()
        tasks_response = [task.create_dict() for task in tasks]

    return jsonify(tasks_response)


@tasks_bp.route("", methods=["POST"])
def post_tasks():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        error_dict = {"details": "Invalid data"}
        return jsonify(error_dict), 400

    new_task = Task.from_json()
    task_response = {"task": new_task.create_dict()}
    return jsonify(task_response), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def get_tasks_by_id(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404

    task_response = {"task": task.create_dict()}
    return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_tasks_by_id(task_id):

    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404
    form_data = request.get_json()

    task.title = form_data["title"]
    task.description = form_data["description"]
    task.iscomplete = None

    db.session.commit()

    task_response = {"task": task.create_dict()}
    return jsonify(task_response), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify(None), 404

    db.session.delete(task)
    db.session.commit()

    delete_message = {
        "details": f'Task {task.task_id} "{task.title}" successfully deleted'}

    return jsonify(delete_message), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def task_complete(task_id):
    if request.method == "PATCH":
        task = Task.query.get(task_id)
        if not task:
            return jsonify(None), 404

        task.completed_at = datetime.datetime.now()
        db.session.commit()

        task.send_task_complete_slack_message()

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def task_incomplete(task_id):
    if request.method == "PATCH":
        task = Task.query.get(task_id)
        if not task:
            return jsonify(None), 404

        task.completed_at = None
        db.session.commit()

        task_response = {"task": task.create_dict()}
        return jsonify(task_response), 200


#
# Start Goals Routes
#


@goals_bp.route("", methods=["GET"])
def get_all_goals():
    title_from_url = request.args.get("title")

    goals = Goal.goal_arguments(title_from_url)
    goals_response = []
    goals_response = [goal.create_dict() for goal in goals]

    if not goals_response:
        goals = Goal.query.all()
        goals_response = [goal.create_dict() for goal in goals]

    return jsonify(goals_response)


@goals_bp.route("", methods=["POST"])
def new_goal():
    request_body = request.get_json()
    if "title" not in request_body:
        error_dict = {"details": "Invalid data"}
        return jsonify(error_dict), 400

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    goal_response = {"goal": new_goal.create_dict()}
    return jsonify(goal_response), 201


@goals_bp.route("/<goal_id>", methods=["GET"])
def get_individual_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify(None), 404

    if request.method == "GET":
        goal_response = {"goal": goal.create_dict()}
        return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def replace_individual_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify(None), 404
    form_data = request.get_json()

    goal.title = form_data["title"]

    db.session.commit()

    goal_response = {"goal": goal.create_dict()}
    return jsonify(goal_response), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify(None), 404
    db.session.delete(goal)
    db.session.commit()

    delete_message = {
        "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}

    return jsonify(delete_message), 200


@goals_bp.route("<goal_id>/tasks", methods=["GET"])
def get_goal_with_tasks(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return jsonify(None), 404

    # goal_response = []
    goal_response = [task.create_dict() for task in goal.tasks]

    response = {"id": goal.goal_id,
                "title": goal.title,
                "tasks": goal_response}
    return jsonify(response), 200


@goals_bp.route("<goal_id>/tasks", methods=["POST"])
def create_goal_with_tasks(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return jsonify(None), 404

    form_data = request.get_json()
    task_ids = form_data["task_ids"]
    for id in task_ids:
        task = Task.query.get(id)
        if not task:
            continue
        task.goal = goal
        db.session.commit()
    
    goal_response = [item.task_id for item in goal.tasks]
    response = {"id": goal.goal_id,
                "task_ids": goal_response}

    return jsonify(response), 200
