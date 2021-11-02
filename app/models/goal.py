from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        """ Converts the Goal object to a dictionary """
        return {
            "id": self.goal_id,
            "title": self.title
        }