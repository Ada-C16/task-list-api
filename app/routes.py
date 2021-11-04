from flask import Blueprint, jsonify, make_response, request, Flask
from app.models.goal import Goal
from app.models.task import Task
from app import db
from datetime import datetime
import os, requests, sys
from ..cli.main import run_cli, delete_all_tasks, change_task_complete_status, delete_task_ui, edit_task, view_task, create_task, print_single_row_of_stars, print_surround_stars, print_all_tasks, print_task, get_task_from_user, make_choice, list_options, OPTIONS
from ..cli.task_list import mark_complete, mark_incomplete, delete_task, update_task, get_task, list_tasks, create_task, parse_response

task_list_bp = Blueprint("task_list", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
welcome_bp = Blueprint("homescreen", __name__)

@welcome_bp.route("", methods=["GET"])
def welcome_screen():
    print("Welcome to Task List CLI")
    print("These are the actions you can take:")
    print_single_row_of_stars()
    list_options()
    run_cli()


@task_list_bp.route("", methods=["GET"])
def get_task_lists():
    """Define an endpoint for get that returns all tasks, optionally presented by a query pram of descending\
        or ascending"""
    query_sort = request.args.get("sort")
    tasks_response = []

    if query_sort == "asc":
        tasks = Task.query.order_by(Task.title)
    elif query_sort == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
            
    for task in tasks:
        tasks_response.append(task.to_dict())

    return make_response(jsonify(tasks_response), 200)

@task_list_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    """Define an endpoing of get id where we return a dict of just that task"""
    task = Task.query.get_or_404(task_id)
    return make_response(jsonify({"task": task.to_dict()}), 200)

@task_list_bp.route("", methods=["POST"])
def create_a_valid_task():
    """Define an endpoint of post, where we can create a new task with all required attributes"""

    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response(jsonify({"details": "Invalid data"}), 400)

    request_body = sanitize_date(request_body)

    new_task = Task(title = request_body["title"],
                    description = request_body["description"],
                    completed_at = request_body["completed_at"])

    add_one_database(new_task)

    return make_response(jsonify({"task": new_task.to_dict()}), 201)

@task_list_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    """Define an endpoint that updates the title or description of the called task"""
    task = Task.query.get_or_404(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    
    db.session.commit()
    return make_response(jsonify({"task": task.to_dict()}), 200)

        

@task_list_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Defines an endpoint for deleting a task"""
    task = Task.query.get_or_404(task_id)
    delete_one_database(task)
    return make_response(jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200)
    

@task_list_bp.route("/<task_id>/<complete_command>", methods=["PATCH"])
def mark_task_complete(task_id, complete_command):
    """Defines an endpoint that will mark a task as complete or incomplete"""
    task = Task.query.get_or_404(task_id)

    if complete_command == "mark_complete":
        task.completed_at = datetime.utcnow()

        # Makes a call the slackbot API
        query = {"channel": "task-notifications", "text": f"CONGRATULATIONS YOU BEAUTIFUL HUMAN!!! You completed task: {task.title}!!!"}
        slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        headers_dict = {"Authorization": f"Bearer {slack_bot_token}"}
        requests.post("https://slack.com/api/chat.postMessage", headers=headers_dict, params=query)

    elif complete_command == "mark_incomplete":
        task.completed_at = None   

    return make_response(jsonify({"task": task.to_dict()}), 200)

@goals_bp.route("", methods=["GET"])
def get_goals():
    """Defines an endpoint that gets all goals, optionally presented by a query pram of descending\
        or ascending"""
    query_sort = request.args.get("sort")
    goals_response = []

    if query_sort == "asc":
        goals = Goal.query.order_by(Goal.title)
    elif query_sort == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()
        
    for goal in goals:
        goals_response.append(goal.to_dict())

    return make_response(jsonify(goals_response), 200)

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    """Defines an endoint that returns all goals"""
    goal = Goal.query.get_or_404(goal_id)
    return make_response(jsonify({"goal": goal.to_dict()}), 200)

@goals_bp.route("", methods=["POST"])
def create_a_valid_goal():
    """Defines an endpoint that creates a valid goal with all required attributes"""
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response(jsonify({"details": "Invalid data"}), 400)
    
    new_goal = Goal(
        title = request_body["title"]
        )
    add_one_database(new_goal)
    return make_response(jsonify({"goal": new_goal.to_dict()}), 201)

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_a_goal(goal_id):
    """Defines an endpoint to delete a goal"""
    goal = Goal.query.get_or_404(goal_id)
    delete_one_database(goal)
    return make_response(jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200)

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_a_goal(goal_id):
    """Defines an endpoint that updates a goal with new information"""
    goal = Goal.query.get_or_404(goal_id)
    request_body = request.get_json()
    goal.title = request_body["title"]
    db.session.commit
    return make_response(jsonify({"goal": goal.to_dict()}), 200)

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_for_goal(goal_id):
    """Defines an endpoint that associates a task with a goal"""
    request_body = request.get_json()
    goal = Goal.query.get_or_404(goal_id)
    for each_task in request_body["task_ids"]:
        each_task = Task.query.get(each_task)
        each_task.fk_goal_id = goal.goal_id
    return make_response(jsonify({"id": goal.goal_id, "task_ids": request_body["task_ids"]}), 200)

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    """Defines an endpoint that returns all tasks associated with a goal """
    goal = Goal.query.get_or_404(goal_id)
    return make_response(goal.to_dict_with_tasks(goal_id), 200)

def sanitize_date(request_body):
    """Verifies that complete_at in correct datetime format"""
    if request_body["completed_at"]:
        try:
            val = request_body["completed_at"]
            type(val) == datetime
        except:
            sys.exit("Completed_at should be in YYYY-MM-DD hh:mm:ss format or null")
    return request_body

def add_one_database(item):
    """Defines a helper function to add an item to database"""
    db.session.add(item)
    db.session.commit()

def delete_one_database(item):
    """Defines a helper function to delete an item from database"""
    db.session.delete(item)
    db.session.commit()
