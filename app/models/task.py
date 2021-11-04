from flask import current_app
from app import db
from sqlalchemy.sql.expression import null
import requests
import os


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_json(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)    
        }

    def to_json_with_goal(self):
        json_info = self.to_json() 
        json_info["goal_id"] = self.goal_id
        return json_info

    @classmethod
    def from_json(cls, request_body):
        return cls(title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"])

    def slack_post(self):
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {os.environ.get('SLACK_API_KEY')}"},
            params={
                "channel": "task-notifications",
                "text": f"Someone just completed the task {self.title}"
            })