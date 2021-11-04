from flask import current_app
from sqlalchemy.orm import backref
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_json(self):
        return {
            "id": self.goal_id,
            "title": self.title,   
        }

    @classmethod
    def from_json(cls, request_body):
        return cls(title=request_body["title"])