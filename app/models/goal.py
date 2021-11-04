from flask import current_app
from app import db
from .task import Task 

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref = "goal", lazy = True) 
    def goal_dict(self):
        return{
            "id":self.goal_id,
            "title":self.title
        }