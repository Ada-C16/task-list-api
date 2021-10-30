from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
    completed_at = db.Column(db.DateTime, nullable = True)
    # difficulty = db.Column(db.Integer)
    


    def to_dict(self):
        """ Converts the task object to a dictionary """
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False
        }