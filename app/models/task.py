from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String)
    task_description = db.Column(db.String)
    task_completed_at = db.Column(db.DateTime, nullable=True)
