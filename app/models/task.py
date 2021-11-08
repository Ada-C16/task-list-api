from flask import current_app
from sqlalchemy.orm import backref
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement= True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id')) #NEW
    goal = db.relationship("Goal", back_populates= "tasks") #NEW

    def is_complete(self):
        return bool(self.completed_at)

    def to_dict(self):
        # if not self.completed_at:
        #     is_complete = False
        # else:
        #     is_complete = True
            
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.is_complete(),
        }