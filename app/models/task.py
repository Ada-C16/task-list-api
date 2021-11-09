from flask import current_app
import requests, os
from app import db



class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)
    is_complete = db.Column(db.Boolean)

    def to_dict(self):  
        return {
            "id": self.task_id, 
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }

    def post_message_on_slack(self):
        url = os.environ.get("URL")
        data = {
            'token': os.environ.get("KEY"),
            'channel': "task_notifications",
            'text': f"Someone just completed the task: {self.title}"
        }
        requests.post(url, data)