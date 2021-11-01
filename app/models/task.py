from flask import current_app
from app import db
import requests
import os


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_dict(self):
        self.is_complete = False if not self.completed_at else True

        task_dict = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.is_complete,
            }
        
        if self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id
        
        return task_dict
    
    def post_slack_message(self):
        url = "https://slack.com/api/chat.postMessage"
        data = {
            'token': os.environ.get(
            "SLACK_API_KEY"),
            'channel': "C02J08B9S0N",
            'text': f"Someone just completed the task: {self.title}"
        }
        requests.post(url, data)