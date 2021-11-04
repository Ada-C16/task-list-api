from flask import app # mistake from instructors, not really needed 
from app import db

# in each model, write single line w/SQL to 

class Task(db.Model):
    __tablename__= "tasks"
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200)) 
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """converts task data to dictionary"""
        return{
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False
        }