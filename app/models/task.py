from flask import current_app, request
from app import db
from dotenv import load_dotenv
from sqlalchemy import desc,asc

#task is a class
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)#autoincrement = True 
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))
    # goal_id = db.relationship("Goal", back_populates="tasks")

    def task_dict(self):
        task_dict = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False if self.completed_at is None else True
        }
        
        if self.goal_id:
            task_dict["goal_id"]=self.goal_id
                
        return task_dict
