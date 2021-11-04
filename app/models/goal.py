from flask import current_app
from sqlalchemy.orm import backref
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        return({
        "id": self.goal_id, 
        "title": self.title
        }) 