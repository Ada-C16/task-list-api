from flask import current_app
from app import db
from .task import Task


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }

    def to_dict_with_tasks(self):
        return {
            "id": self.id,
            "title": self.title,
            "tasks": [task.to_dict() for task in self.tasks]
        }