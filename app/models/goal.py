from flask import current_app
from sqlalchemy.orm import backref
from app import db
from app.models.task import Task


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True) 


    def to_dict(self):
        return {
            "goal_id":self.goal_id,
            "title" : self.title
        }

    def to_dict_with_tasks(self):
        # tasks = Task.query.filter_by(fk_goal_id=f"{goal_id}")
        # tasks_list = []
        # for task in tasks:
        #     tasks_list.append(task.to_dict())
        return{
            "id":self.goal_id,
            # "title":self.title,
            "tasks": [task.to_dict() for task in self.tasks]
        }
    def verbose_goal_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": [task.to_dict() for task in self.tasks]
        }
