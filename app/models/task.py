from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), nullable = False)
    completed_at = db.Column(db.DateTime, nullable = True)
    # I'm not sure about completed_at and is_completed.
    # Is completed_at only for POST, and then is_completed only for responses?

    def to_dict(self):
        if self.completed_at:
            is_complete = True
        else:
            is_complete = False
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": is_complete
        }