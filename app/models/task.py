from flask import current_app
from app import db
# from datetime import datetime



class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description =db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return { 
            "id": self.task_id,
            "title":self.title,
            "description": self.description,
            "is_complete": False if self.completed_at == None else True
        }

    # def task_dict(self): #class_method
    #     return (f"{self.task_id} {self.title} {self.description}")

# self.is_complete = False if not self.completed_at else True