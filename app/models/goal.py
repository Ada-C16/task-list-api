from flask import current_app
from app import db
from .task import Task


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def goal_with_tasks_dict(self):
        return {
            "id": self.goal_id,
            "task_ids": [task.task_id for task in self.tasks]
        }

    def verbose_goal_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": [task.to_dict() for task in self.tasks]
        }

