from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    task_ids = db.relationship('task', backref='Goal')

    def to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            }
        
        return new_dict