from flask.wrappers import Response
from app.models.task import Task
from app import db
from flask import Blueprint, jsonify, make_response, request

# handle_tasks handles GET and POST requests for the /tasks endpoint


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
# Wave 1: Get Tasks: Getting Saved Tasks
    if request.method == "GET":
        sort = request.args.get("sort")
        if sort == "asc":
            tasks = Task.query.order_by(Task.title)
        elif sort == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
#Wave 1: Get Tasks: No Saved Tasks
        tasks_response = []
        for task in tasks:
            has_complete = task.completed_at
            tasks_response.append(
                {
                    "description": task.description,
                    "id": task.task_id,
                    "is_complete": False if has_complete == None else has_complete,
                    "title": task.title,
                }
            )
        return jsonify(tasks_response)
# Wave 1: Create a Task: Valid Task With null completed_at
    elif request.method == "POST":
        request_body = request.get_json()
#Wave 1: Create A Task: Missing Title
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            response_body= {
                "details": "Invalid data"
            }
            return make_response(response_body, 400)

        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()
        
#Wave 1: Create A Task: Valid Task with null completed_at 201 CREATED

        request_body= {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else new_task.completed_at
            }
        }

        return request_body,201

# handle_one_task handles GET,PUT and DELETE requests for the tasks/task_id endpoint
@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task_id = int(task_id)
    task = Task.query.get_or_404(task_id)
#Wave 1: Get One Task: One Saved Task
    if request.method == "GET":
        has_complete = task.completed_at
        task_response={   
                "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if has_complete == None else has_complete,
                
            }
            }
        
        return jsonify(task_response)
#Wave 1: Update Task, #Wave 1 Update Task: No Matching Task
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        

        db.session.commit()
#Wave 1: Update Task 200 OK
        request_body= {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else task.completed_at
            }
        }

        return make_response(request_body, 200)
#Wave 1  Delete Task: Deleting A Task, #Wave 1: Delete Task: No Matching Task
    elif request.method == "DELETE": 
        db.session.delete(task)
        db.session.commit()
        response = {
            "details": f'Task {task.task_id} "{task.title}" successfully deleted'
        }
        json_response = jsonify(response)
        return make_response(json_response, 200)



