from flask import current_app
from app import db
from sqlalchemy.orm import backref

# from app.models.task import Task


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable = False)
    tasks = db.relationship("Task", backref="goal", lazy=True) 


    def to_dict(self):

        return({
        "id": self.goal_id,
        "title": self.title,
        })

    def to_tasks_dict(self):
        return {
            "id": self.goal_id,
            "task_ids": self.tasks
        }

    