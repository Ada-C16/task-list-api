from flask import current_app
from app import db
import datetime

# MAC - Don't forget migrate and upgrade!

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable=True)

    def to_dict(self):
        is_complete = True
        if not self.completed_at: 
            is_complete = False
        
        if not self.goal_id: 
            return({
                "id": self.task_id, 
                "title": self.title, 
                "description": self.description, 
                "is_complete": is_complete
            }) 
        
        else: 
            return({
                "id": self.task_id, 
                "title": self.title, 
                "description": self.description, 
                "is_complete": is_complete,
                "goal_id": self.goal_id
            }) 
        



