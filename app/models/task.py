from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
    completed_at = db.Column(db.DateTime, nullable = True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable = True)
    
    def to_dict(self):
        """ Converts the task object to a dictionary, adds the goal_id if there is one """
        result = {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True if self.completed_at else False
            }
        if self.goal_id is not None:
            result["goal_id"] = self.goal_id
        return result