from flask import current_app
from app import db

# This the table
class Task(db.Model):
    # These are the columns
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
