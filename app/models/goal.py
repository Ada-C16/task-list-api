from app import db
from flask import request, current_app


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", back_populates="goal")

    def create_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title,
        }
