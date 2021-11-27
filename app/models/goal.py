from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    # Make goal_id autoincrement?

    # Have to rename? or use the one from Task model?
    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }