from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship('Task', backref='goal', lazy =True)

    # Structure goal body for responses.
    def goal_body(self):
        goal_body = {
        "id": self.goal_id,
        "title": self.title,
        }
        return goal_body

    # Create response body for a single goal.
    def create_goal_response(self):
        return {"goal": self.goal_body()}