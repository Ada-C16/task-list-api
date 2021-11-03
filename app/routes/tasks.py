from app import db
from app.models.task import Task
from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, abort

task_bp = Blueprint('task', __name__, url_prefix="/tasks")


''' POST task  - this function handles the creation of a task.
    it requests "title", "description" and "completed_at" values to be to successful
'''
@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    try:
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            response_body = {"details": "Invalid data. itle', 'description', 'completed_at' are required"} 
            return make_response(jsonify(response_body), 400)


        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        response_body = {
            "task": new_task.to_dict()
        }
        return make_response(jsonify(response_body),201)

    except Exception:
        abort(400)



'''GET tasks    - this function reads all tasks from databases
                - this function handles searches of tasks by: title
'''
@task_bp.route("", methods=["GET"])
def read_all_tasks():

    sort_by_title_query = request.args.get("sort")
    task_response = []
    try:
        if sort_by_title_query == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif sort_by_title_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        
        else:
            tasks = Task.query.all()
        for task in tasks:
            task_response.append(task.to_dict())     

        return  make_response(jsonify(task_response),200)

    except Exception:
        abort(400)


''' GET <task_id>  - this functions returns a functions when 
                    an unique id is passed in the request body
                    if not found returns 404 error
'''
@task_bp.route("/<task_id>", methods=["GET"])
def read_one_drink(task_id):
    task = get_task_by_id(task_id)

    try:
        if task.goal_id:
            task_response = {"task": task.to_dict_goal_task() }                
            
        else:
            task_response = {"task": task.to_dict() }

        return jsonify(task_response), 200

    except Exception: 
        abort(400)


''' DELETE      - this functions handles the deletion of a task by its id
'''

@task_bp.route("/<task_id>", methods=['DELETE'])
def delete_one_task(task_id):
    task = get_task_by_id(task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        response_body = {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}

        return make_response(response_body, 200)

    except Exception: 
        abort(400)



''' PATCH       - this functions updates a task by its id'''

@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_by_id(task_id)

    try:
        request_body = request.get_json()
        if not request_body: 
            abort(400)

        if "title" in request_body:
            task.title = request_body["title"]
        if "description" in request_body:
            task.description = request_body["description"]
        
        db.session.commit()

        response_body = {
            "task": task.to_dict()
        }
        return make_response(response_body, 200)

    except Exception: 
        abort(400)


# use a dynamic route to handle is complete and else 
# SLACK API
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task =  get_task_by_id(task_id)
    date = datetime.utcnow()
    try:
        if task.completed_at == None:
            task.completed_at = date

        db.session.commit()

        response_body = {
                "task": task.to_dict()} 
        return response_body
    except Exception:
        abort(400)


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task =  get_task_by_id(task_id)

    try:
        task.completed_at = None
        db.session.commit()
        response_body = {
                "task": task.to_dict()} 
        return response_body
    except Exception:
        abort(400)


'''Error Handling'''

@task_bp.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not found"}),404

@task_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "Bad request"}),400

@task_bp.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}),422


''' Helper Functions - 

get_task_by_id - handles 404 errors '''

def get_task_by_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id, description='{Task not found}')


def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f'{parameter_type} must be an integer'}, 400))
