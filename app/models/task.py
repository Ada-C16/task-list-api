from flask import current_app
from app import db
import requests 
import os 

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, default=None, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_json(self, title=None, description=None):
        task_dict = {
            "id": self.task_id,
            "goal_id" : self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False,
        }

        if title:
            task_dict["title"] = title
        if description:
            task_dict["description"] = description 
        if self.completed_at:
            task_dict["is_complete"] = True   

        return task_dict 

    def post_to_slack(self):
        path = "https://slack.com/api/chat.postMessage"
        slack_token = os.environ.get('SLACK_TOKEN')
        query_params = {
        "token": slack_token,
        "channel": "slack-api-test-channel",
        "text": f"Someone just completed the task {self.title}."
        }
        requests.post(path, data=query_params)
