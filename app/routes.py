from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import asc, desc
import datetime
from app.models.goal import Goal
import requests, json
from dotenv import load_dotenv
import os
load_dotenv()


task_bp = Blueprint("task", __name__, url_prefix="/tasks")

goal_bp = Blueprint("goal", __name__, url_prefix="/goals")

def helper_func_convert_a_json_to_dict(json_obj, type_task_or_goal):
    if type_task_or_goal == "task_type":
        task_dict = {
            "id" : json_obj.task_id,
            # "goal_id" : json_obj.goal_id,
            "title" : json_obj.title,
            "description" : json_obj.description,
            "is_complete" : True if json_obj.completed_at else False
        }
        return task_dict

    elif type_task_or_goal == "goal_type":
        goal_dict = {
            "id" : json_obj.goal_id,
            "title" : json_obj.title,   
        }
        return goal_dict


@task_bp.route("", methods=["GET", "POST"])
def handle_a_task():
    if request.method == "GET":
        all_tasks = Task.query.all()
        if not all_tasks:
            return jsonify([]), 200

        sort_query = request.args.get("sort", default="asc")  #**
        if sort_query == "asc":
            all_tasks = Task.query.order_by(asc(Task.title)).all()
        elif sort_query == "desc":
            all_tasks = Task.query.order_by(desc(Task.title)).all()

        tasks_response = []
        for task in all_tasks:
            tasks_response.append(task.convert_a_task_to_dict())
        return jsonify(tasks_response), 200

    elif request.method == "POST":
        request_body = request.get_json()

        try: 
            new_task = Task(title=request_body["title"],
                            description=request_body["description"],
                            completed_at=request_body["completed_at"])
            
            db.session.add(new_task)
            db.session.commit()

            return {"task" : new_task.convert_a_task_to_dict()}, 201
        except KeyError:
            return {
                "details": "Invalid data"
                }, 400


@task_bp.route("/<int:task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task_with_id(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "GET":
        if task and task.goal_id:
            return {"task": task.convert_a_task_to_dict(task.goal_id)}, 200
        else:
            return {"task": task.convert_a_task_to_dict()}, 200

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            task.title = request_body['title']
            task.description = request_body['description']

            db.session.add(task)
            db.session.commit()
            return {    
                "task" : task.convert_a_task_to_dict()
            }
        except KeyError:
            return {
                "message" : "require both title and description"
                }, 400
    
    else:   # Delete
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task.task_id} \"{task.title}\" successfully deleted'}

@task_bp.route("<int:task_id>/<mark_complete_or_incomplete>", methods=["PATCH"])
def mark_a_task_completed_with_id(task_id, mark_complete_or_incomplete):
    task = Task.query.get_or_404(task_id)
    if mark_complete_or_incomplete == "mark_complete": 
        task.completed_at = datetime.date.today()

        token = os.environ.get("SLACK_API_TOKEN")
        url = "https://slack.com/api/chat.postMessage"
        headers = {'Authorization': 'Bearer ' + token}
        
        response = requests.post(url, json= {"Someone just completed the task {task.title}"}, headers={'Authorization': 'Bearer ' + token})

    else:   # mark_incomplete
        task.completed_at = None
    db.session.commit()
    return {"task": task.convert_a_task_to_dict()}


@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        if not goals:
            return jsonify([]), 200
        else:
            response = []
            for goal in goals:
                response.append(goal.convert_a_goal_to_dict())
            return jsonify(response), 200

    else:   #POST
        request_body = request.get_json()
        try:
            new_goal = Goal(title=request_body["title"])

            db.session.add(new_goal)
            db.session.commit()

            return {"goal" : new_goal.convert_a_goal_to_dict()}, 201
        except KeyError:
            return {
                "details": "Invalid data"
                }, 400


@goal_bp.route("/<int:goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_a_goal_with_id(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        return {"goal" : goal.convert_a_goal_to_dict()}

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            goal.title = request_body["title"]

            db.session.commit()
            return {"goal" : goal.convert_a_goal_to_dict()}, 200
        except:
            return make_response("missing require fields")
    
    else:   # DELETE
        db.session.delete(goal)
        db.session.commit()
        return {"details": f'Goal {goal.goal_id} \"{goal.title}\" successfully deleted'}


@goal_bp.route("/<int:goal_id>/tasks", methods=["POST", "GET"])
def relating_a_list_of_taskIDs_to_a_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        tasks_with_specific_goal_id = Task.query.filter_by(goal_id=goal_id).all()
        tasks_list = []
        for task in tasks_with_specific_goal_id:
            tasks_list.append(task.convert_a_task_to_dict(goal_id))

        goal_dict = goal.convert_a_goal_to_dict()
        goal_dict["tasks"] = tasks_list

        return goal_dict
        
        

    else: #POST   
        request_body = request.get_json()
        task_ids_list = request_body["task_ids"]
        for task_id in task_ids_list:
            task = Task.query.get_or_404(task_id)
            task.goal_id = goal_id
        goal.task = task_ids_list
        
        db.session.commit()
        
        return {
            "id" : goal_id,
            "task_ids" : task_ids_list
        }, 200






