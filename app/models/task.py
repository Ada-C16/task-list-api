from flask import current_app
from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    match_goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")

    def to_dict(self):
        response_body = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
            }
        
        if self.match_goal_id:
            response_body["goal_id"] = self.match_goal_id
        
        return response_body