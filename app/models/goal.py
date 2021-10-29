from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    def to_dict(self):
        # is_complete = False if not self.completed_at else True
        return {
            "id": self.goal_id,
            "title": self.title
        }
