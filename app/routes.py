from app import db
from flask import Blueprint, request, abort, jsonify
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    """Retrieve all stored tasks."""
    tasks = Task.query.all()

    task_response = []
    for task in tasks:
        task_response.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        })
        #TODO: Refactor to use to_dict() method

    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    """Retrieve one stored task by id."""
    task = Task.query.get_or_404(task_id)
    return jsonify({"task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }}), 200
        #TODO: Refactor to use to_dict() method

@tasks_bp.route("", methods=["POST"])
def post_task():
    """Create a new task from JSON data."""
    form_data = request.get_json()

    #TODO: Refactor to validation decorator helper method
    mandatory_fields = ["title", "description", "completed_at"]
    for field in mandatory_fields:
        if field not in form_data:
            return jsonify({"details": "Invalid data"}), 400 

    new_task = Task(
        title=form_data["title"],
        description=form_data["description"],
        completed_at=form_data["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    print(new_task.to_dict())
    return {"task": {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": new_task.is_complete
                }
        }, 201
        #TODO: Refactor to use to_dict() method

@tasks_bp.route("/<task_id>", methods=["PUT"])
def put_task(task_id):
    """Updates task by id."""
    # Search database for task by id
    task = Task.query.get_or_404(task_id)
    # Retrieve form data
    form_data = request.get_json()

    # Loops through attributes provided by user
    for key, value in form_data.items():
        # Restricts to attributes that are table columns
        if key in Task.__table__.columns.keys():
            setattr(task, key, value)

    db.session.commit()

    return {"task": {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete
    }}
    #TODO: Refactor to use to_dict() method

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Deletes task by id."""
    task = Task.query.get_or_404(task_id)
    if task:
        return_statement = f"Task {task.id} \"{task.title}\" successfully deleted"
        db.session.delete(task)
        db.session.commit()

        return {
            "details": return_statement
        }, 200