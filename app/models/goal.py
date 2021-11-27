from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable = False)
    tasks = db.relationship("Task", back_populates="goal", lazy=True)

    # Have to rename? or use the one from Task model?
    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }