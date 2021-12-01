from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    # tasks = db.relationship("Task", back_populates="goal", lazy=True)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict_goal(self):
        return {
            "id": self.goal_id,
            "title": self.title,
        }
