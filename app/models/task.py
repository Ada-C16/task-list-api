from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    
    # personalized attributes
    #priority = db.Column(db.Integer, nullable=False)
    #due_date = db.Column(db.DateTime, nullable=True)

    # attributes with defaults
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    completed_at = db.Column(db.DateTime, default=None)
    is_complete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.task_id,
            'title': self.title,
            'description': self.description,
            #'completed_at': self.completed_at,
            #'created_date': self.created_date,
            'is_complete': self.is_complete
        }
