from flask import current_app, jsonify
from app import db
import requests
import os
#from app.models.goal import Goal

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable =True)
    is_complete = db.Column(db.Boolean)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_dict(self):  
        task_dict = {
            "id": self.task_id, 
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        return task_dict
