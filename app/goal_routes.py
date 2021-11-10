from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, jsonify
from sqlalchemy import desc
from datetime import datetime
import requests


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


# goals
@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return jsonify(details="Invalid data"), 400

        new_goal = Goal(
            title=request_body["title"]
        )

        db.session.add(new_goal)
        db.session.commit()

        return jsonify(goal=new_goal.to_json_goal()), 201

    elif request.method == "GET":
        goals = Goal.query.all()
        response_body = []
        for goal in goals:
            response_body.append(goal.to_json_goal())

        return jsonify(response_body), 200


@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_Goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        return jsonify(goal=goal.to_json_goal()), 200

    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        db.session.commit()
        return jsonify(goal=goal.to_json_goal()), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return jsonify(details="Goal 1 \"Build a habit of going outside daily\" successfully deleted"), 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    if request.method == "POST":
        request_body = request.get_json()
        task_list = request_body["task_ids"]

        for task_id in task_list:
            task = Task.query.get(task_id)
            task.goal = goal

        db.session.commit()
        return {
            "id": goal.id,
            "task_ids": task_list
        }, 200

    elif request.method == "GET":
        tasks = goal.tasks
        task_response = []
        for task in tasks:
            task_response.append(task.to_json_task())

        return {
            "id":  goal.id,
            "title": goal.title,
            "tasks": task_response
        }, 200
