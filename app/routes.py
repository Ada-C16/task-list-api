from flask.wrappers import Response
from app.models.task import Task
from app import db
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import date
import os
import requests
from dotenv import load_dotenv
from app.models.goal import Goal

# handle_tasks handles GET and POST requests for the /tasks endpoint


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
def valid_int(number,parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error":f"{parameter_type} must be an int"},400))

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
# Wave 1: Get Tasks: Getting Saved Tasks
    if request.method == "GET":
        sort = request.args.get("sort")
        if sort == "asc":
            tasks = Task.query.order_by(Task.title)
        elif sort == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
#Wave 1: Get Tasks: No Saved Tasks
        tasks_response = []
        for task in tasks:
            has_complete = task.completed_at
            tasks_response.append(
                {
                    "description": task.description,
                    "id": task.task_id,
                    "is_complete": False if has_complete == None else has_complete,
                    "title": task.title,
                }
            )
        return jsonify(tasks_response)
# Wave 1: Create a Task: Valid Task With null completed_at
    elif request.method == "POST":
        request_body = request.get_json()
#Wave 1: Create A Task: Missing Title
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            response_body= {
                "details": "Invalid data"
            }
            return make_response(response_body, 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()
        
#Wave 1: Create A Task: Valid Task with null completed_at 201 CREATED


        return jsonify({"task":new_task.to_dict()}),201
# handle_one_task handles GET,PUT and DELETE requests for the tasks/task_id endpoint
@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    valid_int(task_id,"task_id")
    task = Task.query.get_or_404(task_id)
# Wave 1: Get One Task: One Saved Task
    if request.method == "GET":
        has_complete = task.completed_at
        task_response={   
                "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if has_complete == None else has_complete,
                
            }
            }
        
        return jsonify(task_response)
#Wave 1: Update Task, #Wave 1 Update Task: No Matching Task, Update Task 200 OK
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        

        db.session.commit()
        return jsonify({"task":task.to_dict()}),200

#Wave 1  Delete Task: Deleting A Task, #Wave 1: Delete Task: No Matching Task
    elif request.method == "DELETE": 
        db.session.delete(task)
        db.session.commit()
        response = {
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }
        json_response = jsonify(response)
        return make_response(json_response, 200)

def slack_bot(title):
    query_path = {
        "channel": "melinda-bot",
        "text": f"Someone completed the task {title}"
    }
    header = {
        "Authorization": f"Bearer {os.environ.get('BOT')}"
    }
    response = requests.post("https://slack.com/api/chat.postMessage",params = query_path, headers = header)
    return response.json()


#Wave 3 
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_completed_task(task_id):
    valid_int(task_id,"task_id")
    task = Task.query.get_or_404(task_id)
    task.completed_at = date.today()
    db.session.commit()
    slack_bot(task.title)
    return jsonify ({"task":task.to_dict()}),200
    

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"]) 
def handle_incompleted_task(task_id):
    valid_int(task_id,"task_id")
    task = Task.query.get_or_404(task_id)
    task.completed_at = None
    db.session.commit()
    return jsonify ({"task":task.to_dict()}),200


# Wave 5 Creating a Goal Model Blueprint
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# Wave 5 Create A Goal: Valid Goal
@goals_bp.route("", methods=["POST"])
def handle_post_goals():

    request_body = request.get_json()

    if "title" not in request_body:
        response_body= {
            "details": "Invalid data"
        }
        return make_response(response_body, 400)

    new_goal = Goal(
        title = request_body["title"]
    )
    db.session.add(new_goal)
    db.session.commit()
    response_body = {
        "goal": {
        "id": new_goal.goal_id,
        "title": new_goal.title
        }
    }

    return jsonify(response_body), 201

# Wave 5 Get Goals: Getting Saved Goals
@goals_bp.route("", methods=["GET"])
def handle_get_goals():
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append(
        {
            
            "id": goal.goal_id,
            "title": goal.title, 
        }
            )
        return jsonify(goals_response)



# Wave 5 Update Goal: Update Goal/No Matching Goal
@goals_bp.route("/<goal_id>", methods=["PUT"])
def handle_update_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    form_data = request.get_json()
    if "title" not in form_data:
        response_body= {
            "details": "title required"
        }
        return make_response(response_body, 400)
    goal.title = form_data["title"]

    db.session.commit()
    return jsonify({"goal":goal.to_dict()}),200

# Wave 5 Deleting A Goal: Deleting A Goal/No Matching Goal
@goals_bp.route("/<goal_id>", methods=["DELETE"])
def handle_delete_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    response = {
            "details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }
    json_response = jsonify(response)
    return make_response(json_response, 200)










