from flask import current_app
from sqlalchemy.orm import relationship
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref='task', lazy=True)

    def to_dict(self):
        if self.tasks:
            return {
                "id": self.goal_id,
                "title": self.title,
                "tasks": [task.to_dict() for task in self.tasks]
                }
        else:
            return {
                "id": self.goal_id,
                "title": self.title
                }