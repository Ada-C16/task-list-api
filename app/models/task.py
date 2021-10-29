from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)

    def to_dict(self):
        if not self.completed_at:
            completed_at = False
        new_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": completed_at,
            }
        
        return new_dict