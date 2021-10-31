import re
from app import db
from app.models.task import Task 
from flask import Blueprint, jsonify, make_response, request 
from app.models.goal import Goal
from datetime import datetime


tasks_bp = Blueprint("tasks",__name__, url_prefix=("/tasks" ))

@tasks_bp.route("", methods=["GET"])
def get_task():
    sort_query = request.args.get("sort")
    if sort_query == "desc": 
        task = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
        task = Task.query.order_by(Task.title.asc())
    else: 
        task = Task.query.all()
    task_response = [task.to_dict()for task in task]
    return jsonify(task_response),200


@tasks_bp.route("", methods=[ "POST"])
def handle_task_post():
    if request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
                    
                    return{
                        "details":"Invalid data"
                    },400


        new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return {
            "task":{
                "id":new_task.task_id,
                "title":new_task.title,
                "description": new_task.description,
                "is_complete":False if new_task.completed_at == None else True
            }
        },201
       
 
@tasks_bp.route("/<task_id>",methods=["GET","PUT","DELETE"])
def handle_task_id(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return ("", 404)

    if request.method == "GET":
        return {
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description": task.description,
                "is_complete":False if task.completed_at == None else True
            }
        }
    if request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()
       
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":False if task.completed_at == None else True
            }
        }),200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()   
        return jsonify({
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
            }),200

#wave 3 
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_mark_complete(task_id):
    task = Task.query.get(task_id) 
    
    if task is not None: 
        if request.method == "PATCH":
        
            task.completed_at = datetime.now()
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":bool(task.completed_at)
            }
        }),200

    else: 
        return (""), 404
    
#headers 
#json 
#request 
#insert API key and hide it 
#os.environ.get()
@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_mark_incomplete(task_id):
    task = Task.query.get(task_id) 

    if task is not None:
        if request.method == "PATCH":
                task.completed_at = None
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":bool(task.completed_at)
            }
        }),200

    else: 
        return (""), 404

    