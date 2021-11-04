from flask import current_app
from app import db
#from app.models.Goal import Goal

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True )
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=True)

    def to_dict(self):
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False
        }

        if self.goal_id:
            result["goal_id"]=self.goal_id
        return result
    