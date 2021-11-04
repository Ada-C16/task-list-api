from re import T
from flask import current_app
from sqlalchemy.orm import backref, lazyload
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True)
    # tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }
