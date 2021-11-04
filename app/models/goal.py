from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy = True)


    def goal_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def tasked_goal(self):
        task_dicts =[]
        for task in self.tasks:
            task_dicts.append(task.tasked_dict())
        return{
            "id": self.goal_id,
            "title": self.title,
            "tasks":task_dicts
        }
                