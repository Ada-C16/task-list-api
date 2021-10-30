from app import db
from app.models import task
from app.models.task import Task
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
            response_body = {"details": "Invalid data"} 
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


'''GET tasks - this function reads all tasks from databases
                - this function handles searches of tasks by: title
'''
@task_bp.route("", methods=["GET"])
def read_all_tasks():

    task_title_query = request.args.get("title")
    task_response = []
    try:
        if task_title_query:
            tasks = Task.query.filter_by(title= task_title_query)
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
        task_response = {"task": task.to_dict() }
        return jsonify(task_response), 200

    except Exception: 
        abort(400)


''' DELETE - this functions handles the deletion of a task by its unique id
'''

@task_bp.route("/<task_id>", methods=['DELETE'])
def delete_one_task(task_id):
    task = get_task_by_id(task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        response_body = {"details": f'Task {task.task_id} "Go on my daily walk 🏞" successfully deleted'}

        return make_response(response_body, 200)

    except Exception: 
        abort(400)



''' PATCH - this functions updates a task by its id'''

@task_bp.route("/<task_id>", methods=["PATCH"])
def update_task(task_id):
    task = get_task_by_id(task_id)






'''Error Handling'''

@task_bp.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not found"}),404


@task_bp.errorhandler(400)
def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}),400




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


