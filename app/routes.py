import datetime, requests, os
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from dotenv import load_dotenv

load_dotenv()

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

# creates a Task
@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return make_response(
        {"task":(new_task.to_dict())}, 201
    )
    
# reads all created Tasks
@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_tasks():
    tasks_response = []

    if request.args.get("sort") == "asc":
        tasks = Task.query.order_by(Task.title)
    elif request.args.get("sort") == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    for task in tasks:
        tasks_response.append(task.to_dict())
    return jsonify(tasks_response), 200

# single Task: read
@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_task(task_id):
    task = Task.query.get_or_404(task_id)

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: update
@tasks_bp.route("/<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: delete
@tasks_bp.route("/<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response(
        {"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}, 200
    )

# single Task: update (patch request to mark task as complete)
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"], strict_slashes=False)
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = datetime.datetime.now()
    db.session.commit()

    # call the slack API using helper function
    post_to_slack_task_notifications_channel(f"Someone just completed the task {task.title}")

    return make_response(
        {"task":(task.to_dict())}, 200
    )

# single Task: update (incompleted tasks stay incompleted)
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"], strict_slashes=False)
def incomplete_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = None
    db.session.commit()

    return make_response(
        {"task":(task.to_dict())}, 200
    )

def post_to_slack_task_notifications_channel(text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": os.environ.get("TANYAB0T_TOKEN")}
    data = {
        "channel": os.environ.get("TASK_NOTIFICATIONS_CHANNEL_ID"),
        "text": text
    }
    requests.post(url, headers=headers, data=data)

# creates a  Goal
@goals_bp.route("", methods=["POST"], strict_slashes=False)
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    new_goal = Goal(
        title = request_body["title"]
    )

    db.session.add(new_goal)
    db.session.commit()

    return make_response(
        {"goal":(new_goal.to_dict())}, 201
    )

# reads all created Goals
@goals_bp.route("", methods=["GET"], strict_slashes=False)
def get_goals():
    goals_response = []

    goals = Goal.query.all()

    for goal in goals:
        goals_response.append(goal.to_dict())
    return jsonify(goals_response), 200

# single Task: Goal
@goals_bp.route("/<goal_id>", methods=["GET"], strict_slashes=False)
def get_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    return make_response(
        {"goal":(goal.to_dict())}, 200
    )

# single Goal: update
@goals_bp.route("/<goal_id>", methods=["PUT"], strict_slashes=False)
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response(
            {"details": f"Invalid data"}, 400
        )

    goal.title = request_body["title"]

    db.session.commit()

    return make_response(
        {"goal":(goal.to_dict())}, 200
    )

# single Goal: delete
@goals_bp.route("/<goal_id>", methods=["DELETE"], strict_slashes=False)
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response(
        {"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}, 200
    )

# send a list of Task IDs to a Goal
@goals_bp.route("/<goal_id>/tasks", methods=["POST"], strict_slashes=False)
def post_tasks_to_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()
    task_ids = request_body["task_ids"]

    # loops through task_ids list, which are the IDs of Tasks that client want to associate with this specific goal 
    for task in task_ids: 
        # uses each task_id to query the Task object that needs to be updated with match_goal_id foreign key 
        task_to_add_to_goal = Task.query.get_or_404(task)
        # uses goal_id from Goal queried above, assigns value to the goal_id foreign key of each task to add
        # loops through given task_ids until each task in the post request has been updated
        task_to_add_to_goal.match_goal_id = goal.goal_id 
        
    db.session.commit()

    return make_response({"id": goal.goal_id, "task_ids": task_ids}, 200)

# getting Tasks of one Goal
@goals_bp.route("/<goal_id>/tasks", methods=["GET"], strict_slashes=False)
def read_tasks_for_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    goal_and_tasks = []

    tasks = Task.query.filter_by(match_goal_id=goal_id)

    for task in tasks:
        goal_and_tasks.append(task.to_dict())

    response_body = goal.to_dict(goal_and_tasks)

    return make_response(response_body, 200)