from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    pass
