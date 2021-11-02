from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    task_ids = db.relationship('Task', back_populates='Goal', lazy = True)

    def to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            "task_ids" : self.task_ids
            }
        
        return new_dict