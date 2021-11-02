from flask import current_app
from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, default=None)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")

    

    def to_dict(self):
        result =  {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False,
        }
        if self.goal_id is not None:
            result["goal_id"]=self.goal_id
        return result 

 