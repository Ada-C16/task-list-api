from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    # Default is not required
    completed_at = db.Column(db.DateTime, default=None, nullable=True)


    def to_dict(self):
        # if self.completed_at.null():
        # self.is_complete = False
        # self.is_complete = True

        return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at),
            }
        