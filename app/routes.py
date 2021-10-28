from app import db
from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    # POST REQUESTS
    if request.method == "POST":

        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            
            return {"details": "Invalid data"}, 400

        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        new_task_response = {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at is not None
        }

        return jsonify(new_task_response), 201

    # GET REQUESTS
    elif request.method == "GET":
        title_query = request.args.get("title")
        description_query = request.args.get("description")
        if title_query:
            tasks = Task.query.filter(Task.title.contains(title_query))
        elif description_query:
            tasks = Task.query.filter(Task.description.contains(description_query))
        else:
            tasks = Task.query.all()

        task_response = {}
        for task in tasks:
            task_response.append(
               {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.completed_at is not None
                }
            )
 
        if task_response == []:
            return 200
        return jsonify(task_response), 200

# GET, PUT, DELETE ONE AT A TIME
@tasks_bp.route("/task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task_at_a_time(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(task_id), 404

    if request.method == "GET":
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }, 200

    if request.method == "PUT":
        if task is None:
            return jsonify(task_id), 404
    
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body:
            return make_response("Invald Request", 400)

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        return jsonify(task_id), 201

    if request.method == "DELETE":
        if task is None:
            return jsonify(task_id), 404

        db.session.delete(task_id)
        db.session.commit()

        return jsonify(task_id)

        