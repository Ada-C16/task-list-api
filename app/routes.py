from flask import Blueprint , jsonify, request , make_response
from app import db
from app.models.task import Task 

tasks_bp = Blueprint("tasks", __name__ , url_prefix="/tasks")

@tasks_bp.route("", methods =["POST","GET"])
def manage_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        try:
            new_task = Task(
                title = request_body["title"],
                description= request_body["description"],
                completed_at = request_body["completed_at"]
            )
            #add new task before response body to get an id value
            db.session.add(new_task)
            db.session.commit()
            response_body = {
                "task":{
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": True if new_task.completed_at is not None else False
                }
            }
            return jsonify(response_body), 201
        except KeyError:
            return {"details":"Invalid data"}, 400

    elif request.method == "GET":
        request_title = request.args.get("title")
        if request_title: #if request_title
            tasks = Task.query.filter_by(title=request_title)
        else:
            tasks = Task.query.all()
        response = []
        for task in tasks:
            response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at is None else True
            })
        return jsonify(response)
    pass


@tasks_bp.route("/<task_id>", methods =["GET","PUT", "DELETE"])
def manage_task(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return  make_response("", 404) 

    if request.method == "GET":
        response_body = {
                "task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at is not None else False
                }
            }
        return jsonify(response_body), 200 

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        # task.completed_at = request_body["completed_at"]
        db.session.commit()
        response_body = {
                "task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at is not None else False
                }
            }
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        response_body = {
            "details":f"Task {task.task_id} \"{task.title}\" successfully deleted"
        }
        return jsonify(response_body), 200
