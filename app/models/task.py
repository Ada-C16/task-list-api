from app import db
from flask import current_app

#Defining a model for Task
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True) 
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable = True)

    def to_dict(self):
        '''Convert data to a dictionary'''
        if self.goal_id == None:
            task_dict = {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True if self.completed_at else False
            }
        else:
            task_dict = {
                "id": self.task_id,
                "goal_id": self.goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True if self.completed_at else False
            }
        return task_dict