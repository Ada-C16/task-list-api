from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))

    def to_dict(self):
        if self.goal_id == None:
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": True if self.completed_at else False
            }
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else False,
            "goal_id": self.goal_id
        }
    @classmethod
    def from_json(self, json):
        return Task(
            title=json["title"],
            description=json["description"],
            completed_at=json["completed_at"]
        )
