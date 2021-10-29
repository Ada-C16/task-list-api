from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, default=None)
    is_complete = db.Column(db.Boolean, default=False)

def to_dict(self):
    new_dict = {
        "id": self.id,
        "title": self.title,
        "description": self.description,
        "completed_at": self.completed_at,
        "is_complete": self.is_complete,
        }
    
    return new_dict