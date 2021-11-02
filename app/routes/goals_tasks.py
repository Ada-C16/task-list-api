from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request, abort
from app.routes.goals import get_goal_by_id, goal_bp
from app.routes.tasks import task_bp
from datetime import datetime




