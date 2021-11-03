from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify,request, make_response
from datetime import datetime
import slack
import os
from tests import test_wave_06

# client = slack.webclient(token=os.environ['OAUTH_TOKENS'])
# tasks_bp = Blueprint("tasks",__name__,url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__,url_prefix="/goals")
@goals_bp.route("/goals/1/tasks", methods=["POST"])
def create_goal(goal_id):
    request_body = request.get_json()
    print(request_body)
    # tasks = Task.query.filter_by(Task.goal_id ==1)
   
    goal = Goal.query.get(goal_id)
    new_task = Task(id = request_body["id"],
                    task_ids = request_body['task_ids']
                    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"goal":new_goal.to_dict()}),201