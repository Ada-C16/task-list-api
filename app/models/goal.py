from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    def to_dict(self):
        response_body = {
            "id": self.goal_id,
            "title": self.title
            }
        
        return response_body