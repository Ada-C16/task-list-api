from flask import Blueprint, request, make_response, jsonify
from flask_sqlalchemy import model
from app import db
from app.models.task import Task
from datetime import datetime
import requests
import os


from tests.conftest import completed_task


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()

        else:
            tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            if not task.completed_at:
                tasks_response.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False
                })
            else:
                tasks_response.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete
                })
        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        if request_body.get("title") and request_body.get("description"): 
            """and request_body.get("completed_at")"""
            if request_body.get("completed_at")==None:
                new_task = Task(title=request_body["title"],
                                description=request_body["description"])
                db.session.add(new_task)
                db.session.commit()
                response_value = {"task":{
                        "id": new_task.task_id,
                        "title": new_task.title,
                        "description": new_task.description,
                        "is_complete": False
                }}
            else:
                new_task = Task(title=request_body["title"],
                            description=request_body["description"],
                            completed_at=datetime.now())
                db.session.add(new_task)
                db.session.commit()
                response_value = {"task":{
                        "id": new_task.task_id,
                        "title": new_task.title,
                        "description": new_task.description,
                        "is_complete": True
                    }}
        else:
            return make_response({"details":"Invalid data"}, 400)

        
        return make_response(response_value, 201)
        
    # task_by_title = Task.query.filter_by(title=new_task.title)

    # if not new_task.completed_at:
    #     response_value = {"task":{
    #         "id": len(Task.query.all()),
    #         "title": new_task.title,
    #         "description": new_task.description,
    #         "is_complete": False
    #     }}

    #     return make_response(response_value, 201)
    # else:
    #     response_value = {"task":{
    #         "id": len(Task.query.all()),
    #         "title": new_task.title,
    #         "description": new_task.description,
    #         "is_complete": new_task.is_complete
    #     }}

    #     return make_response(response_value, 201)

    # return make_response({"task":request_body}, 201)






@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        if not task.completed_at:
            response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }}

            return make_response(response_value, 200)
        else:
            response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            }}

            return make_response(response_value, 200)
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        if form_data.get("completed_at"):
            task.completed_at = datetime.now()

        db.session.commit()

        if not task.completed_at:
            response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }}

            return make_response(response_value, 200)
        else:
            response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
            }}
            return make_response(response_value, 200)

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'},200)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)

    task.completed_at = datetime.now()

    response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
    }}
    url= 'https://slack.com/api/chat.postMessage'
    header_values = {'AUTHORIZATION': os.environ.get("AUTHORIZATION")}
    slack_values = {"text" : f"You just finished {task.title}",
                    "channel" : "task list api"
    }
    requests.post(url, headers=header_values, params=slack_values)
    db.session.commit()

    return (make_response(response_value, 200))

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)

    task.completed_at = None

    response_value = {"task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
    }}


    db.session.commit()
    return (make_response(response_value, 200))