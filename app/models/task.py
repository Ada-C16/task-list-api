from flask import current_app
from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True)

# - We can assume that the value of each task's `completed_at` attribute will be `None`, until wave 3. (Read below for examples)
# - We can assume that the API will designate `is_complete` as `false`, until wave 3. (Read below for examples)