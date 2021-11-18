from flask import current_app
from app import db
from sqlalchemy.orm import backref

from app.models.task import Task


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref='goal', lazy=True)
#Task.query.get(goal_id) = a list of tasks with that matching goal_id
    def to_dict(self):
        return{
            "id": self.goal_id,
            "title": self.title
        }
    
    def to_dict_with_tasks(self, goal_id):
        tasks = Task.query.filter_by(fk_goal_id=f"{goal_id}")
        task_list = []
        for task in tasks:
            task_list.append(task.to_dict())
        return{
            "id":self.goal_id,
            "title":self.title,
        }