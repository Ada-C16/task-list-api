from flask import current_app
from app import db
from datetime import datetime


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(64))
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        if not self.completed_at:
            return {"task": {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": False
            }
            }
        
        return {"task": {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at
        }}

