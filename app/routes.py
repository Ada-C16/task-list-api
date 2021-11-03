from flask import Blueprint, jsonify, request, make_response
from app.models.task import Task, task_schema
from app.models.goal import Goal, goal_schema
from app import db
import jsonschema
from jsonschema import validate
from app import slack_key
import requests

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')
goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

'''TASK ROUTES'''
@tasks_bp.route('', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'GET':
        # if request.args.get("description"):
        #     tasks = Task.query.filter_by(description=request.args.get("description"))
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        # if not tasks:
        #     return make_response(jsonify({'message': 'No tasks found'}), 404)
        return jsonify([task.to_dict() for task in tasks]), 200

    elif request.method == 'POST':
        request_body = request.get_json()
        if not validate_json(request_body, task_schema):
            return make_response(jsonify({"details": "Invalid data"}), 400)
        
        if isinstance(request_body, list):
            for task in request_body:
                new_task = Task(
                    title=task['title'],
                    description=task['description'],
                    completed_at = task['completed_at']
                    # priority=task['priority'],
                    # due_date=task['due_date']
                )
                db.session.add(new_task)
                return jsonify({"task": task.to_dict()} for task in request_body), 201
        else:
            new_task = Task(
                title=request_body['title'],
                description=request_body['description'],
                completed_at = request_body['completed_at']
                # priority=request_body['priority'],
                # due_date=request_body['due_date']
            )
            db.session.add(new_task)
            db.session.commit()
            return jsonify({"task": new_task.to_dict()}), 201

@tasks_bp.route('/<int:id_num>', methods=['GET', "PUT", "DELETE"])
def handle_single_task(id_num):
    task = Task.query.get_or_404(id_num)
    if not task:
        return make_response(jsonify({'message': 'Task not found'}), 404)

    if request.method == 'GET':
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == 'PUT':
        request_body = request.get_json()
        for key, value in request_body.items():
            if key in Task.__table__.columns.keys():
                setattr(task, key, value)
        db.session.commit()
        return jsonify({"task": task.to_dict()}), 200

    elif request.method == "DELETE":
        task_id = task.to_dict()['id']
        task_title = task.to_dict()['title']

        db.session.delete(task)
        db.session.commit()
        return jsonify({'details': f'Task {task_id} "{task_title}" successfully deleted'}), 200

@tasks_bp.route('/<int:id_num>/mark_complete', methods=['PATCH'])
def mark_complete(id_num):
    task = Task.query.get_or_404(id_num)
    if not task:
        return make_response(jsonify({'message': 'Task not found'}), 404)
    task.completed_at = db.func.current_timestamp()
    task.is_complete = True
    db.session.commit()

    # lets make a call to my slack bot
    slack_bot(task.title)

    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route('/<int:id_num>/mark_incomplete', methods=['PATCH'])
def mark_incomplete(id_num):
    task = Task.query.get_or_404(id_num)
    if not task:
        return make_response(jsonify({'message': 'Task not found'}), 404)
    task.completed_at = None
    task.is_complete = False

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200

'''GOAL ROUTES'''
@goals_bp.route('', methods=['GET', 'POST'])
def handle_goals():
    if request.method == 'GET':
        goals = Goal.query.all()
        return jsonify([goal.to_dict() for goal in goals]), 200

    elif request.method == 'POST':
        request_body = request.get_json()
        if not validate_json(request_body, goal_schema):
            return make_response(jsonify({"details": "Invalid data"}), 400)
        
        if isinstance(request_body, list):
            for goal in request_body:
                new_goal = Goal(
                    title=goal['title']
                )
                db.session.add(new_goal)
                return jsonify({"goal": goal.to_dict()} for goal in request_body), 201
        else:
            new_goal = Goal(
                title=request_body['title']
            )
            db.session.add(new_goal)
            db.session.commit()
            return jsonify({"goal": new_goal.to_dict()}), 201

@goals_bp.route('/<int:id_num>', methods=['GET', "PUT", "DELETE"])
def handle_single_goal(id_num):
    goal = Goal.query.get_or_404(id_num)
    if not goal:
        return make_response(jsonify({'message': 'Goal not found'}), 404)
    
    if request.method == 'GET':
        return jsonify({"goal": goal.to_dict()}), 200

    elif request.method == 'PUT':
        request_body = request.get_json()
        for key, value in request_body.items():
            if key in Goal.__table__.columns.keys():
                setattr(goal, key, value)
        db.session.commit()
        return jsonify({"goal": goal.to_dict()}), 200

    elif request.method == "DELETE":
        goal_id = goal.to_dict()['id']
        goal_title = goal.to_dict()['title']

        db.session.delete(goal)
        db.session.commit()
        return jsonify({'details': f'Goal {goal_id} "{goal_title}" successfully deleted'}), 200

@goals_bp.route('/<id_num>/tasks', methods=['GET', 'POST'])
def create_goal_task_relationship(id_num):
    goal = Goal.query.get_or_404(id_num)
    request_body = request.get_json()

    if not goal:
        return make_response(jsonify({'message': 'Goal not found'}), 404)
    
    if request.method == 'POST':
        task_ids = request_body['task_ids']

        if not task_ids:
            return make_response(jsonify({'message': 'No task ids provided'}), 400)

        for task_id in task_ids:
            task = Task.query.get_or_404(task_id)
            if not task:
                return make_response(jsonify({'message': 'Task not found'}), 404)
            #task.goal_id = goal.goal_id
            goal.tasks.append(task)
            db.session.commit()
        
        return jsonify({
            "id": goal.goal_id,
            "task_ids": goal.task_ids()
            }), 200

    elif request.method == 'GET':
        return jsonify(goal.to_dict(True)), 200

'''HELPER FUNCTIONS'''
def validate_json(json_data, comparison):
    try:
        validate(instance=json_data, schema=comparison)
    except jsonschema.exceptions.ValidationError as err:
        #print(err)
        return False
    return True

def slack_bot(task_title):
    url = "https://slack.com/api/chat.postMessage"
    payload = {
    "token" : slack_key,
    "channel" : "task-notifications",
    "text" : f"Someone just completed {task_title}"
    }
    return requests.post(url, data=payload).json()

