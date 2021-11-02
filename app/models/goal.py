from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
        return {
            'id': self.goal_id,
            'title': self.title
        }

goal_schema = {
    "title": "Goal Information",
    "description": "Contains goal related information",
    "required": ["title"],
    "type": ["object"],
    "properties": {
        "title": {
            "type": "string"
        },
        "goal_id": {
            "type": "number"
        }
    }
}