from flask import current_app
from app import db
import datetime


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    # is_complete = db.Column(db.Boolean)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    # relationship
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_dict(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            # "is_complete": True if self.completed_at == True else False
            "is_complete": bool(self.completed_at)
        }
    
    def to_dict_for_goal(self):
        return {
            "id": self.task_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
        }