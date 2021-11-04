from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    related_tasks = db.relationship("Task", backref="goal")

    def to_dict(self):
        return({
        "id": self.goal_id, 
        "title": self.title
        }) 