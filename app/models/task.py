from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True) 
    is_complete = db.Column(db.Boolean)
    # completed_at can be empty/null which means that a task is not completed
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable = True)
    
    def to_dict(self):
        if not self.completed_at:
            self.is_complete = False 
        else:
            self.is_complete = True
        dictionary = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.is_complete
        }
        if self.goal_id: 
            dictionary["goal_id"] = self.goal_id
            
        return dictionary