from flask import Blueprint, jsonify, request, make_response, abort
from app.models.task import Task
from app import db

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
def get_all_tasks():
    title_query = request.args.get('title') #query params for wave2
    if title_query:
    # filter_by returns a list of objects/ records that match the query params
        books = Task.query.filter_by(title = title_query)
    else:
        tasks = Task.query.all()
    # query_all return list of objects. loop through lists and add to empt list, task_response
    # as requested formatted JSON objects
    task_response = []
    
    for task in tasks:
        is_complete = task.completed_at is not None
        task_response.append({
        'id': task.task_id,
        'title': task.title,
        'description': task.description,
        'is_complete': is_complete})
    
    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
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
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({'details': 
        f'Task {task.task_id} "{task.title}" successfully deleted'}, 200)
                                    
