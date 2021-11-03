
from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(50))
    description=db.Column(db.String(200))
    completed_at=db.Column(db.DateTime, nullable=True)#default=None
    
    def to_dict(self):
        if self.completed_at == None:
            return {
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False
        }

        else:
            return{
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True
        }
        

