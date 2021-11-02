from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))

    def is_complete(self):
        is_complete = True
        if not self.completed_at:
            is_complete = False
        return is_complete

    def to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.is_complete()
            }
        
        if self.goal_id != None:
            new_dict['goal_id'] = self.goal_id
        
        return new_dict