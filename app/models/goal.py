from flask import current_app
from app import db
from app.models.Task import Task

class Goal(db.Model):
    __tablename__ = 'goal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    #these are not just IDs, like a list of numbers...they are objects of type Task
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
            return {
                "id": self.id,
                "title": self.title,
            }


    def goal_tasks_to_dict(self):
        mytasks = Task.query.all(self[0].tasks)
        mylist = []
        for thing in mytasks:
            mylist.append(thing.id)

        return {              
            "id": self.id,
            "task_ids": mylist
        }