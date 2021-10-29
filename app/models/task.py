from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, default=None)

def to_dict(self):
    new_dict = {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "completed_at": self.completed_at
        }
    
    return new_dict