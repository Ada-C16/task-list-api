from flask import current_app
from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")


# Create helper function for task dictionary
    def get_task_dict(self):
        if self.completed_at:
            complete = True
        else:
            complete = False
        
        if self.goal_id:
            return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": complete
            }     
        else:
            return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": complete
            }
# Create helper function for "completed_at"


# Guard Clause Function (Catch None) - Utiities File


    