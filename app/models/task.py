from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, auto_increment= True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db(db.DateTime, default= False)


def to_dict(self):
    return {
        'task_id': self.id,
        'title': self.title,
        'description': self.description,
        'is_complete': True if self.completed_at else False,
            }