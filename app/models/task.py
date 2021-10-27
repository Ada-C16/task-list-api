from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    priority = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
