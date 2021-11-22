from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable = True)
    #goal = db.relationship('Goal', back_populates = 'tasks', lazy = True)  unnecessary because we have backref in goal model

    def to_string(self):
        return f"{self.id}: {self.title} Description: {self.description} Completed at: {self.completed_at}"
    
    def combo_dict(self): 
        return {
            "id": self.id, 
            "goal_id": self.goal_id,
            "title": self.title, 
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
    
