from flask import Blueprint, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
