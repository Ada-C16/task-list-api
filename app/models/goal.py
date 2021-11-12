from re import T
from flask import current_app
from flask.helpers import make_response
from sqlalchemy.orm import backref, lazyload
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def create_task_list(self):
        task_list = []
        for task in self.tasks:
            task_list.append(task.to_dict())
        return task_list

    def to_dict_with_tasks(self):
        return {
                    "id": self.goal_id,
                    "title": self.title,
                    "tasks": [task.to_dict() for task in self.tasks]
                }
