from flask import current_app
from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)


    # Create Helper Function for completed_at/is_complete
    # def task_completion(self, completed_at):
    #     if completed_at == datetime.utcnow():
    #         "is_complete" = True
    #     else:
    #         "is_complete" = False
    #     pass


    