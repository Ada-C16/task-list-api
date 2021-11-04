from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)

    def check_if_completed(self):
        if self.completed_at:
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.check_if_completed()
        }

    def update_from_dict(self, data):
        # Loops through attributes provided by user
        for key, value in data.items():
            # Restricts to attributes that are table columns
            if key in Task.__table__.columns.keys():
                setattr(self, key, value)