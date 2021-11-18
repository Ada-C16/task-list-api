from flask import current_app
from app import db
from sqlalchemy.orm import backref




class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(50))
    description=db.Column(db.String(200))
    completed_at=db.Column(db.DateTime, nullable=True)#default=None
    goal_id=db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    
    def to_dict(self):
        if self.goal_id:
            return {
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False,
            "goal_id": self.goal_id
        }

        else:
            return{
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False
        }
        

