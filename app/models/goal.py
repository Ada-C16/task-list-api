from flask import current_app
from app import db
from app.models.task import Task



class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    # list holding all tasks associated with this goal
    tasks = db.relationship('Task', back_populates='goal')

    def to_dict(self):
        if self.tasks == None:
            return {
                "id": self.goal_id,
                "title": self.title,
            }
        else:
            return {
                "id": self.goal_id,
                "task_ids": self.tasks.task_id
            }


    def to_dict_plus_tasks(self):
        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": [
                Task.to_dict()
            ]
        }
