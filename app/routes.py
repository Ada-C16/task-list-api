from flask import Blueprint, jsonify, request, make_response, abort
from app.models.task import Task
from app import db
from sqlalchemy import desc
from datetime import date, time, datetime

# assign tasks_bp to the new Blueprint instance
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
def post_one_task():
    request_body = request.get_json()
    if 'title' not in request_body or 'description' \
    not in request_body or 'completed_at' not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    else:
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
        # using is_completed to hold Boolean value of datetime which is the data type
        # for new_task.completed_at, essentially converting from Null to False
        is_complete = new_task.completed_at is not None
        return make_response({"task": {"id": new_task.task_id,
                                        "title": new_task.title,
                                        "description": new_task.description,
                                        "is_complete": is_complete}}, 201)
                                    
@tasks_bp.route("", methods=["GET"])
def working_with_all_tasks():
    title_query = request.args.get('title') #query params for wave2
    order_by_query = request.args.get('sort')
    if title_query:
    # filter_by returns a list of objects/ records that match the query params
    
        tasks = Task.query.filter_by(title = title_query)
    # what part of the Task.query is actually accessing the DB?
    elif order_by_query == 'asc':
        tasks = Task.query.order_by(Task.title).all()
    # query_all return list of objects. loop through objects and add to empt list, task_response
    # as requested formatted JSON objects
    elif order_by_query == 'desc':
        tasks = Task.query.order_by(desc(Task.title)).all()
    # this else covers any search for all tasks, without any query params
    else:
        tasks = Task.query.order_by(Task.title).all()
    
    task_response = []
    
    for task in tasks:
        is_complete = task.completed_at is not None
        task_response.append({
        'id': task.task_id,
        'title': task.title,
        'description': task.description,
        'is_complete': is_complete})
    
    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE", "PATCH"])
def CRUD_one_task(task_id):
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
# couldn't figure out another way to return no response body, researched abort
        abort(404) 
# returning the object's info in the desired data structure format
    is_complete = task.completed_at is not None
    if request.method == "GET":
        return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
    elif request.method == "PUT":
    # form data is a local variable to hold the body of the HTTP request
        form_data = request.get_json()
    # reassigning attributes of the task object using the dict values that came over 
    # in the request body
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = task.completed_at

        db.session.commit()

        return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
    elif request.method == "PATCH":
        form_data = request.get_json()
        if "title" in form_data:
            task.title = form_data["title"]
        if "description" in form_data:
            task.description = form_data["description"]
        
        db.session.commit()
        return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
        
@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    time_stamp = datetime.now()
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
        abort(404) 
    else:
        task.completed_at = time_stamp
    db.session.commit()
    is_complete = task.completed_at is not None
    return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get(task_id) #either get Task back or None
    if task is None:
        abort(404) 
    else:
        task.completed_at = None
    db.session.commit()
    is_complete = task.completed_at is not None
    return make_response({"task": {"id": task.task_id,
                                    "title": task.title,
                                    "description": task.description,
                                    "is_complete": is_complete}}, 200)
    
                                    
