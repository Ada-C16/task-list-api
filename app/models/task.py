from flask import current_app
from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        if not self.completed_at:
            self.completed_at = None
        return({
        "id": self.task_id,
        "title": self.title,
        "description": self.description,
        "is_complete": self.completed_at == False,
        })

