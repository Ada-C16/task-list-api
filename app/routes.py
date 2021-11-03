from flask.wrappers import Response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, timezone
import os
from slack import WebClient
from slack.errors import SlackApiError

#create the blueprint for the endpoints
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

#Create a Task: Valid Task With null completed_at
@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    
    if request_body["completed_at"] is not None:
        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])
    else:
        new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at = None)

    db.session.add(new_task)
    db.session.commit()

    response = {}
    task = {}
    task['id'] = new_task.task_id
    task['title'] = request_body["title"]
    task['description'] = request_body["description"]
    if request_body["completed_at"] is not None:
        task['is_complete'] = True
    else:
        task['is_complete'] = False
    response['task'] = task
    print(response)

    return make_response(response, 201)

#Get Tasks: Getting Saved Tasks
@tasks_bp.route("", methods=["GET"])
def get_tasks():

    sort_query = request.args.get("sort")
    if(sort_query == "asc"):
        tasks = Task.query.order_by(Task.title).all()
    elif(sort_query == "desc"):
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()
    
    response = []

    for task in tasks:
        task_dict = {}
        task_dict["id"] = task.task_id
        task_dict["title"] = task.title
        task_dict["description"] = task.description
        
        if task.completed_at is not None:
            task_dict["is_complete"] = True
        else:
            task_dict["is_complete"] = False

        response.append(task_dict)

    return jsonify(response)

#Get a Task
@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response("Not Found", 404)
    
    response = {}
    task_dict = {}

    task_dict["id"] = task.task_id
    task_dict["title"] = task.title
    task_dict["description"] = task.description
    
    if task.completed_at is not None:
        task_dict["is_complete"] = True
    else:
        task_dict["is_complete"] = False

    if task.goal_id is not None:
        task_dict["goal_id"] = task.goal_id
    
    response["task"] = task_dict
    return response

#Update One Task
@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    
    form_data = request.get_json()
    task.title = form_data["title"]
    task.description = form_data["description"]
    #task.completed_at = form_data["completed_at"]

    db.session.commit()
    
    response = {}
    task_dict = {}

    task_dict["id"] = task.task_id
    task_dict["title"] = task.title
    task_dict["description"] = task.description

    if task.completed_at is not None:
        task_dict["is_complete"] = True
    else:
        task_dict["is_complete"] = False

    response["task"] = task_dict
    return make_response(response, 200)
    #return make_response(f"Task #{task.task_id} successfully updated")




# Delete One Task
@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    
    if task is None:
        return make_response(f"Task {task_id} not found", 404)

    response = {"details": f'Task {task.task_id} "{task.title}" successfully deleted' }
    db.session.delete(task)
    db.session.commit()

    return make_response(response, 200)


#Mark Complete        
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):

    # #
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    # #

    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)

    #first get the task
    response_json = {}
    task_dict = {} 

    #check the competion of the task
    # if task.completed_at is None:
    #     #update it 
    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    task_dict["is_complete"]= True 

    task_dict["id"]= task.task_id
    task_dict["title"]= task.title
    task_dict["description"]= task.description
    
    response_json["task"] = task_dict

    print(task.completed_at)

    # 
    try:
        response = client.chat_postMessage(
            channel="task-notifications",
            text=f"Someone just completed the task {task_dict['title']} :tada:")
    
    except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    # 
    return make_response(response_json, 200)

#Mark Incomplete 
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)

    response = {}
    task_dict = {} 

    # if task.completed_at is not None:
    task.completed_at = None
    
    task_dict["id"]= task.task_id
    task_dict["title"]= task.title
    task_dict["description"]= task.description
    task_dict["is_complete"]= False
    
    response["task"] = task_dict

    print(task.completed_at)

    return make_response(response, 200)

###########

#Create a Goal
@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_goal = Goal(title=request_body["title"])
    db.session.add(new_goal)
    db.session.commit()

    response = {}
    goal = {}
    goal['id'] = new_goal.goal_id
    goal['title'] = request_body["title"]

    response["goal"] = goal
    
    return make_response(response, 201)

#Get Goals
@goals_bp.route("", methods=["GET"])
def get_goals():

    sort_query = request.args.get("sort")
    if(sort_query == "asc"):
        goals = Goal.query.order_by(Goal.title).all()
    elif(sort_query == "desc"):
        goals = Goal.query.order_by(Goal.title.desc()).all()
    else:
        goals = Goal.query.all()
    
    response = []

    for goal in goals:
        goal_dict = {}
        goal_dict["id"] = goal.goal_id
        goal_dict["title"] = goal.title
        
        response.append(goal_dict)

    return jsonify(response)

#Get a Goal
@goals_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return make_response("Not Found", 404)
    
    response = {}
    goal_dict = {}

    goal_dict["id"] = goal.goal_id
    goal_dict["title"] = goal.title
    
    response["goal"] = goal_dict
    return response

#Update One Goal
@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)
    
    form_data = request.get_json()
    goal.title = form_data["title"]

    db.session.commit()
    
    response = {}
    goal_dict = {}

    goal_dict["id"] = goal.goal_id
    goal_dict["title"] = goal.title

    response["goal"] = goal_dict
    return make_response(response, 200)


# Delete One Goal
@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return make_response(f"Goal {goal_id} not found", 404)

    response = {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted' }
    db.session.delete(goal)
    db.session.commit()

    return make_response(response, 200)

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_goal(goal_id):

    #you would want to get the tasks for each id sent in and set their goals ids to this goal's id
    #then format a json with the task ids present to show the goal id and its tasks

    goal = Goal.query.get(goal_id) #we grabbed the goal for the provided id

    if goal is None: #error checking
        return make_response("", 404)
    
    request_body = request.get_json() #grab form data
    task_ids = request_body["task_ids"] #storing the list in a cleaner variable reference
    
    for task in range(len(task_ids)): #for each index in this list
        this_task = Task.query.get(task_ids[task]) #get one task at a time
        this_task.goal_id = goal.goal_id #set its goal id to the id of this goal
        db.session.commit()

    response = {"id": goal.goal_id, "task_ids": task_ids}
    return make_response(response, 200)


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_specific_goals(goal_id): 

    #get the goal cuz we need its details
    #get tasks that have that goal id 
    #if no tasks have that goal id, return a specific response 

    goal = Goal.query.get(goal_id) #grab the specific goal

    if goal is None:
        return make_response("", 404)

    tasks = Task.query.filter(Task.goal_id==goal_id).all() 
    response = {"id": goal.goal_id, "title": goal.title, "tasks": []}

    for task in tasks:
        task_dict = {}
        task_dict["id"] = task.task_id 
        task_dict["goal_id"] = task.goal_id
        task_dict["title"] = task.title
        task_dict["description"] = task.description
        if task.completed_at is not None:    
            task_dict["is_complete"] = True
        else:
            task_dict["is_complete"] = False
    
        response["tasks"].append(task_dict)
    
    return make_response(response, 200)

    
    # request_body = request.get_json() #grab form data
    # task_ids = request_body["task_ids"] #storing the list in a cleaner variable reference
    # response = {"id": goal.goal_id, "task_ids": task_ids, "tasks": []}

    # for task in range(len(task_ids)): #for each index in this list
    #     this_task = Task.query.get(task_ids[task]) #get one task at a time
    #     task_dict = {}
    #     task_dict["id"] = this_task.task_id 
    #     task_dict["goal_id"] = this_task.goal_id
    #     task_dict["title"] = this_task.title
    #     task_dict["description"] = this_task.description
    #     if this_task.completed_at is not None:    
    #         task_dict["is_complete"] = True
    #     else:
    #         task_dict["is_complete"] = False
    
    #     response["tasks"].append(task_dict)

    #return make_response(response, 200)    


# @goals_bp.route("/<goal_id>/tasks", methods=["GET"])
# def get_tasks_for_specific_goals(goal_id): 
#     #given a specific goal, we want to find the task with that goal id
#     goal = Goal.query.get(goal_id) #grab the specific goal

#     if goal is None:
#         return make_response("", 404)
    
#     request_body = request.get_json() #grab form data
#     task_ids = request_body["task_ids"] #storing the list in a cleaner variable reference
#     response = {"id": goal.goal_id, "task_ids": task_ids, "tasks": []}

#     for task in range(len(task_ids)): #for each index in this list
#         this_task = Task.query.get(task_ids[task]) #get one task at a time
#         task_dict = {}
#         task_dict["id"] = this_task.task_id 
#         task_dict["goal_id"] = this_task.goal_id
#         task_dict["title"] = this_task.title
#         task_dict["description"] = this_task.description
#         if this_task.completed_at is not None:    
#             task_dict["is_complete"] = True
#         else:
#             task_dict["is_complete"] = False
    
#         response["tasks"].append(task_dict)

#     return make_response(response, 200)  