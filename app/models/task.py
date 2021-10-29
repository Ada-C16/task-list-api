from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True) # nullable=True means that if we don't make a POST request with a "completed_at" in the request body, SQL will fill in completed_at for us with 'null'

