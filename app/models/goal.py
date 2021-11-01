from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    __tablename__ = "goals"
    tasks = db.relationship("Task", back_populates="goals")

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }
