from app import db
from flask import request, current_app
from dotenv import load_dotenv
import requests
import os


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))
    # goal = db.relationship("Goal", back_populates="tasks")

    def create_dict(self):
        complete_status = True if self.completed_at else False
        if self.goal_id is not None:
            return {
                "id": self.task_id,
                "goal_id": self.goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": complete_status,
            }
        else:
            return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": complete_status,
            }

    def send_slack_message(self):
        load_dotenv()

        data = {"token": os.environ.get("SLACK_TOKEN"),
                "channel": os.environ.get("CHANNEL_ID"),
                "text": f"Someone just completed the task {self.title}"}
        url = os.environ.get("SLACK_URL")
        requests.post(url, data)

    @classmethod
    def from_json(cls):
        request_body = request.get_json()

        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"]
                        )
        db.session.add(new_task)
        db.session.commit()

        return new_task
