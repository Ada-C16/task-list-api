from flask import current_app
from app import db
import requests
import os


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable =True)
    is_complete = db.Column(db.Boolean)

    def to_dict(self):  
        task_dict = {
            "id": self.task_id, 
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        return task_dict
