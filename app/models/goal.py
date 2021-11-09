from flask import current_app
from app import db
from app.models.task import Task



class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    # list holding all tasks associated with this goal
    tasks = db.relationship('Task', back_populates='goal')

    def to_dict(self):
        if self.tasks == []:
            return {
                "id": self.goal_id,
                "title": self.title,
            }
        else:
            return {
                "id": self.goal_id,
                "task_ids": self.tasks
            }


    def to_dict_plus_tasks(self):
        task_dicts = []
        for task in self.tasks:
            task_dicts.append(Task.to_dict(task))
        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": task_dicts
        }


        
