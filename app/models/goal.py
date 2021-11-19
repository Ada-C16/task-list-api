from flask import current_app
from sqlalchemy.orm import backref
from app import db
from .task import Task


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    task = db.relationship("Task", backref="goal", lazy=True, uselist=True)

    def to_dict(self):  
        return {
            "id": self.goal_id, 
            "title": self.title,
        }
        
    def task_list(self):
        task_list = []

        for task in self.tasks:
            task_list.append(task.to_dict())

        return task_list
