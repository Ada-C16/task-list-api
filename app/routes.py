from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
tasks_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")



@tasks_bp.route("",methods=["POST", "GET"])
def handle_tasks():
    
    # rturns statement ifsomething is not entered
    
    # get response body inJSON
    if request.method == "POST":
        request_body = request.get_json()

        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            response_body = {
                'details': 'Invalid data'
            }
            return make_response(jsonify(response_body), 400)
        new_task = Task(title=request_body["title"],
            description=request_body["description"], 
            completed_at=request_body["completed_at"])

    # add andcommit newtask

        db.session.add(new_task)
        db.session.commit()

        return {"task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete" : (False
            if new_task.completed_at == None else True)
            }},201
    elif request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter_by(title=title_query)
        else:
            tasks = Task.query.all()

        sort_query = request.args.get("sort")
    
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()) 
        else:
            tasks = Task.query.all()

        task_response = []
        for task in tasks:
            task_response.append({
                        "id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": (False
            if task.completed_at == None else True)})
        return jsonify(task_response)
            
        
        
@tasks_bp.route("/<task_id>",methods=["GET", "PUT","DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"Task {task_id} not found", 404)
    elif request.method == "GET":
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : (False
            if task.completed_at == None else True)
            }},200
    elif request.method == "PUT":
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body:
            return { "message: Requires a title and description and completion status"}, 400
        task.title = request_body["title"]
        task.description = request_body["description"]
        

        # save action and return what you created
        db.session.add(task)
        db.session.commit()
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : (False
            if task.completed_at == None else True)
            }},200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {"details":f'Task {task.task_id} "{task.title}" successfully deleted'}
        # get a return response


@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def complete_task(task_id):
    task = Task.query.get(task_id)
    
    
    if task is None:
            return make_response("", 404)
    
    
    if request.method == "PATCH":
        
        
        task.completed_at = datetime.now()
        
        
        db.session.commit()

        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : True
            }}
    
@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def incomplete_task(task_id):
    task = Task.query.get(task_id)
    
    
    if task is None:
            return make_response("", 404)
    
    
    if request.method == "PATCH":
        task.completed_at = None
        db.session.commit()
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete" : False
            }}
    
    

