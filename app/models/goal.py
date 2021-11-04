from flask import app
from app import db


class Goal(db.Model):
    __Table__name__ = "goals"
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    tasks = db.relationship("Task", backref = "goal", lazy = True)
    
    def to_dict(self):
        return{
            "id": self.goal_id, 
            "title": self.title
        }
