from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = "Tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime,nullable=True)

    def to_dict(self):
        if not self.completed_at:
            is_complete = False
        else:
            is_complete =True
        return ({"task": {"id": self.task_id, 
                "title": self.title,
                "description": self.description,
                "is_complete": is_complete}})