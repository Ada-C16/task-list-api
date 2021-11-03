from flask import current_app
from sqlalchemy.orm import backref
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")
    
 

    def to_dict(self):
        
        is_complete = False if self.completed_at == None else True
        if self.goal_id:
            return {
                "id" : self.task_id,
                "title" : self.title,
                "description" : self.description,
                "is_complete":is_complete,
                "goal_id":self.goal_id
                }
        else:
            return {"id" : self.task_id,
                "title" : self.title,
                "description" : self.description,
                "is_complete":is_complete,
                }
        

    def to_complete(self):
        return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":True,
            }
    def to_incomplete(self):
        return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":False,
            }


      