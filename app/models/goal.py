from flask import current_app
from sqlalchemy.orm import backref
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    # genres = db.relationship("Genre", secondary="books_genres", backref="books")
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        if self.list_of_task_ids():
            
            return{
                
                    "id": self.id,
                    "title": self.title,
                    "tasks_ids": self.list_of_task_ids()
                    }
        else:
            return{
                "id": self.id,
                "title": self.title
            }

    def list_of_task_ids(self):
        task_ids = [task.id for task in self.tasks]
        return task_ids

    def task_list(self):
        list = []
        for task in self.tasks:
            list.append(task.to_dict)

        return list


