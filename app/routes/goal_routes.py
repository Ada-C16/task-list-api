from flask import Blueprint, request, make_response, jsonify, abort
from app.models.goal import Goal
from app import db
from datetime import date, datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')