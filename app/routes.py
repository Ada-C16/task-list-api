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
                    "id": task.id,
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
            return jsonify ({
                "details": "Invalid data"
            }), 400


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
                "id": task.id,
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
            "details": f'Task {task.id} "{task.title}" successfully deleted'
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
        return jsonify ( {
            "details": "Invalid data"
        }), 400

    new_goal = Goal(
        title = request_body["title"]
    )
    db.session.add(new_goal)
    db.session.commit()
    

    return jsonify({"goal":new_goal.to_dict()}), 201

# Wave 5 Get Goals: Getting Saved Goals
@goals_bp.route("", methods=["GET"])
def handle_goals():
    goals = Goal.query.all()
    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())
    return jsonify(goals_response), 200
# @goals_bp.route("", methods=["GET"])
# def handle_get_goals():
#         goals = Goal.query.all()
#         goals_response = []
#         for goal in goals:
#             goals_response.append(goal.to_dict())
#         # {
            
#         #     "id": goal.goal_id,
#         #     "title": goal.title
#         # }
#             #)
#         return jsonify(goals_response), 200



# Wave 5 Update Goal: Update Goal/No Matching Goal
@goals_bp.route("/<goal_id>", methods=["PUT", "GET"])
def handle_update_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        return jsonify({"goal":goal.to_dict()}),200
    elif request.method == "PUT":
        form_data = request.get_json()
        if "title" not in form_data:
            return jsonify( {
                "details": "title required"
            }), 400
            
        goal.title = form_data["title"]

        db.session.commit()
        return jsonify({"goal":{"goal_id":goal.id, "title":goal.title}}),200

# Wave 5 Deleting A Goal: Deleting A Goal/No Matching Goal
@goals_bp.route("/<goal_id>", methods=["DELETE"])
def handle_delete_one_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return jsonify( {
            "details": f"Goal {goal_id} \"{goal.title}\" successfully deleted"
        }),200
    # json_response = jsonify(response)
    # return make_response(json_response), 200 


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_goal(goal_id):
    valid_int(goal_id,"goal_id")
    request_body = request.get_json()
    goal = Goal.query.get_or_404(goal_id)
    task_ids = request_body["task_ids"]
    for task_id in task_ids:
        task = Task.query.get(task_id)
        goal.tasks.append(task)
        db.session.commit()
    return jsonify({"id":goal.id, "task_ids": [task.id for task in goal.tasks]}),200

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    valid_int(goal_id,"goal_id")
    goal = Goal.query.get_or_404(goal_id)
    response_body = {"id":goal.id,
        "title":goal.title,
        "tasks":goal.task_list() 
    }
    print(response_body)
    return jsonify(response_body),200
















# def handle_goals_tasks(goal_id):
#     valid_int(goal_id,"goal_id")
#     goal = Goal.query.get_or_404(goal_id)
#     # if request.method == "POST":
#     request_body = request.get_json()

#     if "task_ids" not in request_body:
#             return jsonify( {
#                 "details": "task_ids required"
#             }), 400  
        
#         # tasks_with_relations = []
#     task_ids = request_body["task_ids"]
#     for task_id in task_ids:
        

#             # tasks_with_relations.append(task_id)
#         task = Task.query.get(task_id)
        
#         if task == None:
#             # TODO: change this back to correct response
#             return jsonify ({"details": "there is no tasks"}), 400
#         goal.tasks.append(task)
#         # task.goal_id = goal.goal_id

#         db.session.commit()
#         return jsonify({"id":goal.id, "task_ids":[task.id for task in goal.tasks]}), 200

#         #     response_body= {
#         #         "id": goal.goal_id,
#         #         "task_ids": tasks_with_relations
                
#         #     }

#         # return (response_body), 200
# @goals_bp.route("/<goal_id>/tasks", methods=["GET"])
# def get_tasks_for_goal(goal_id):
    
#     goal = Goal.query.get(goal_id)
#         # task_with_relationship_goals = goal.tasks
#         # task_list = []
#         # if task_with_relationship_goals:
            
#             # for thing in task_with_relationship_goals:
#                 # task_object = {}
#                 # value_if_true if condition else value_if_false
#                 # completed = '' if thing.is_complete == '' else thing.is_complete
#                 # task_object["id"]= thing.task_id
#                 # task_object["goal_id"]=goal_id
#                 # task_object["title"]=thing.title
#                 # task_object["description"]=thing.description
#                 # # task_object["is_complete"]=completed
#                 # task_list.append(task_object)


#     response_body = {
#         "id": goal_id,
#         "title": goal.title,
#         "tasks": goal.task_list()
#     }

#     return jsonify(response_body), 200













