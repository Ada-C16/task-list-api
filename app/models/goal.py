from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    task_ids = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title
            }
        
        if self.task_ids != []:
            new_dict['task_ids'] = self.task_ids

        return new_dict