from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint
from flask import Blueprint, jsonify, request
from datetime import datetime
import requests
import os  # module to read environment
from dotenv import load_dotenv  # make .env values visable for OS to see
from sqlalchemy import insert #??
load_dotenv()  # I'm not sure if I need this function

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# *****  Wave 1 & Wave 2 (POST & GET - sorting task's titles)  *********


@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    sort_title_query = request.args.get("sort")
    if sort_title_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_title_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()

    response_body = [task.to_dict() for task in tasks]
    return jsonify(response_body), 200


@tasks_bp.route("", methods=["POST"])
def task_create():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    # collecting the values
    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    # return the response to our client
    response_body = {"task": new_task.to_dict()}
    return jsonify(response_body), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def task_get(task_id):
    task = Task.query.get_or_404(task_id)  # providing the task_id
    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
def task_put(task_id):
    task = Task.query.get_or_404(task_id)
    form_data = request.get_json()

    task.title = form_data["title"]
    task.description = form_data["description"]

    db.session.commit()
    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def task_delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
    }), 200


# *****  Wave 3 (PATCH for complete and incomplete task)  *********


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def task_handle_incomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = None
    db.session.commit()

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200

# *****  Wave 3 (PATCH) & 4 (Slack's Bot)  *********


def task_slack_bot(title):
    query_path = {"channel": 'task-notifications', "text": title}
    header = {"Authorization": f"{os.environ.get('BOT')}"}  # metadata
    response = requests.post('https://slack.com/api/chat.postMessage',
                            params=query_path, headers=header)  # (url, param, headers)
    print("Check to see if this works?")
    return response.json()  # return the response in json


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def task_handle_complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = datetime.utcnow()

    db.session.commit()
    task_slack_bot(task.title)

    response_body = {"task": task.to_dict()}
    return jsonify(response_body), 200


# *****  Wave 5  *********
@goals_bp.route("", methods=["POST"])
def goal_create():
    request_body = request.get_json()
    if "title" not in request_body:
        return jsonify({"details": "Invalid data"}), 400

    # collecting the value(s)
    new_goal = Goal(title=request_body["title"])

    # add and update database
    db.session.add(new_goal)
    db.session.commit()

    # return the response to our client
    response_body = {"goal": new_goal.dict()}
    return jsonify(response_body), 201


@goals_bp.route("", methods=["GET"])
def handle_goals():
    goals = Goal.query.all()
    response_body = [goal.dict() for goal in goals]
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def goal_get(goal_id):
    goal = Goal.query.get_or_404(goal_id)  # providing the task_id
    response_body = {"goal": goal.dict()}
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def goal_put(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    form_data = request.get_json()

    goal.title = form_data["title"]

    db.session.commit()
    response_body = {"goal": goal.dict()}
    return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def goal_delete(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return jsonify({
        "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
    }), 200

# *****  Wave 6  *********

@goals_bp.route("/<goal_id>/tasks", methods=["POST"]) # do we use goals or goals_dp
def post_goals_tasks(goal_id):
    
    goal = Goal.query.get(goal_id)

    if goal is None:
        return jsonify("Not Found"), 404
    
    request_body = request.get_json() # {"task_ids": [1, 2, 3]}
    
    # HOW to assign Tasks to goal_id
    tasks_list = [] #class instances
    for task_id in request_body["task_ids"]:
        tasks_list.append(Task.query.get(task_id))
        
    goal.tasks = tasks_list
    

    # Need to update database after inserting values into Task/Goal Table?
    # db.session.add()
    db.session.commit()
    
    tasks_ids_list = [] #task id
    for task in goal.tasks:
        tasks_ids_list.append(task.task_id)

    response_body = {
        "id": goal.goal_id,
        "task_ids": tasks_ids_list
    }
    
    return jsonify(response_body), 200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goals_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id) #

    tasks_list = []

    for task in goal.tasks:
        tasks_list.append({
            "id": task.task_id,
            "goal_id": goal.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
    })
    
    response_body = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks_list
    }
    #check to see goal id, if goal id then retrun tasks_list
    #if not then return response_body

    return jsonify(response_body), 200


    # return jsonify(response_body), 200


    # goal = Goal.query.get_or_404(goal_id)
    # request_body = request.get_json()

    # tasks_ids_list = []
    # for task in goal.tasks:
    #     tasks_ids_list.append(task.task_id)
    
    # response_body = {
    #     "id": goal.goal_id,
    #     "tasks_ids": tasks_ids_list
    # }
    
    # return jsonify(response_body), 200

"""
TODO: learn how to switch endpoints on the same method's request
def handle_complete_task(task_id):
    # if task is None or form_data is None:
    # return jsonify("Not Found"), 404
    task = Task.query.get_or_404(task_id) #or
    # request_body = request.get_json()

    # TODO - switching endpoints:
    # mark_complete = Task.args.get_or_404("mark_complete")
    # mark_incomplete = Task.args.get_or_404("mark_incomplete")
    # query = Task.query
    # if mark_complete:
    #     query = query.filter(Task.task_id.ilike(f"{mark_complete}"))
    #     if "title" in request_body:
    #         task.title = request_body["title"]
    #     elif "description" in request_body:
    #         task.description = request_body["description"]
    #     elif "completed_at" in request_body:
    #         task.complete_at = request_body["completed_at"]

    # if mark_incomplete:
    #     query = query.filter(Task.task_id.ilike(f"{mark_incomplete}"))
    #     if "title" in request_body:
    #         task.title = request_body["title"]
    #     elif "description" in request_body:
    #         task.description = request_body["description"]
    #     elif "completed_at" in request_body:
    #         task.complete_at = request_body["completed_at"]

    # if "title" in request_body:
    #     task.title = request_body["title"]
    # elif "description" in request_body:
    #     task.description = request_body["description"]
    # elif "completed_at" in request_body:
    #     task.complete_at = request_body["completed_at"]
    # if task is None:
    #     return jsonify(None), 404
    task.completed_at = datetime.today()
    db.session.commit()
    return jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False if task.completed_at == None else True
            # "is_complete": task.completed_at is None
        }
    }), 200

"""
    # # HOW to assign Tasks to goal_id
    # # GUESS #1 - I'm guessing how to insert array values to gold_id columns
    # values = request_body["task_ids"]
    # for value in values:
    #     Goal.insert().values(value)
    
    # # GUESS #2  
    # #   insert into goal (goal_id) value (respnse_body)
    # for value in request_body:
    #     Goal.insert().values(value) # ? 
    
    # #GUESS #3
    # # HERE are a few thoughts?
    # Goal.insert().values(request_body)
    # Goal.insert().values()


    # return jsonify({"task": {
    #     "id": task.task_id,
    #     "title": task.title,
    #     "description": task.description,
    #     "is_complete": task.compoleted_at is not None
    # }

    # }), 200

# wave 3 before working on wave 4
# @tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
# def handle_complete_task(task_id):
#     task = Task.query.get_or_404(task_id)
#     task.completed_at = datetime.utcnow()

#     db.session.commit()
#     return jsonify({
#         "task": {
#             "id": task.task_id,
#             "title": task.title,
#             "description": task.description,
#             "is_complete": task.completed_at is not None

#         }
#     }), 200
