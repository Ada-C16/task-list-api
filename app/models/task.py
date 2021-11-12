from flask import current_app
from app import db
from datetime import datetime
"""
In a one to many relationship, the table on the many side of the relationship (Task), called the child table, 
contains a field which references the primary key of the table on the one side of the relationship (Goal), called the parent. 
"""


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    # nullable=True means that if we don't make a POST request with a "completed_at" in the request body, SQL will fill in completed_at for us with 'null'
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey(
        "goal.goal_id"), nullable=True)
