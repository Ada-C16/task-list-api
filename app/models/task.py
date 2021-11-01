from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_json_w1(self):
        return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at)
        }

    def to_json_w3_complete(self):
        return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": True

        }

    def to_json_w3_incomplete(self):
        return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": False

        }
