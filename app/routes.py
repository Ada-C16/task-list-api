from flask import Blueprint, jsonify, request, make_response
from flask.globals import session
from app import db
from app.models.Task import Task
from sqlalchemy import asc, desc


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST","GET"], strict_slashes=False)
def create_task():
    if request.method == "POST":

        request_body = request.get_json()
        if ("title" not in request_body) or ("description" not in request_body) or ("completed_at" not in request_body):
            return {"details": "Invalid data"}, 400
        else:
            new_task = Task(title=request_body['title'], description=request_body['description'], completed_at=request_body['completed_at'])
            db.session.add(new_task)
            db.session.commit()
            if request_body['completed_at'] == None:
                return make_response({"task":new_task.to_dict()}), 201
            else:    
                return make_response({"task":new_task.to_dict()}), 200
    elif request.method == "GET":
        if "sort" in request.args:
            title_sorter = request.args.get("sort")
            if title_sorter == "asc":
                tasks_list = Task.query.order_by(Task.title.asc()).all()
            elif title_sorter == "desc":
                tasks_list = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks_list = Task.query.all()
        response = []
        for my_task in tasks_list:
            response.append(my_task.to_dict())
        return jsonify(response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"], strict_slashes=False)
def get_task(task_id):
    task_id = int(task_id)
    my_task = Task.query.get(task_id)
    if request.method == "GET":
        if my_task is None:
            return "", 404
        else:
            return make_response({"task":my_task.to_dict()}), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        try:
            my_task.title = request_body["title"]
            my_task.description = request_body["description"]
            if "completed_at" in request_body :
                my_task.completed_at = request_body["completed_at"]
            db.session.commit()        
            return make_response({"task":my_task.to_dict()}), 200
        except AttributeError as ae:
            return make_response("", 404)

    elif request.method == "DELETE":
        if my_task is None:
            return "", 404
        else:        
            db.session.delete(my_task)
            db.session.commit()
            myResponse = 'Task ' + str(task_id) + ' "' + my_task.title + '" successfully deleted'
            return make_response({"details":myResponse}), 200



