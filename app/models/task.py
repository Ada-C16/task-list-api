from app import db
from flask import request, current_app
from dotenv import load_dotenv
import requests
import os
from sqlalchemy import desc, asc


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))

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

    def send_task_complete_slack_message(self):
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

    @classmethod
    def task_arguments(cls, name_from_url):
        if name_from_url:
            tasks = Task.query.filter_by(name=name_from_url).all()
            if not tasks:
                tasks = Task.query.filter(Task.name.contains(name_from_url))
        sort_query = request.args.get("sort")
        if sort_query == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        elif sort_query == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        else:
            tasks = Task.query.all()
        return tasks
