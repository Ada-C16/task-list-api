from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    # completed_at can be empty/null BUT if empty/null
    # that means the task is not completed. 
    completed_at = db.Column(db.DateTime)
    # or should this be coded like this:
    # completed_at = db.Column(db.DateTime, default=None) 
    # then would I write more conditionals here to say something like:
    # if not completed_at:
        #task is complete? 
        #otherwise task is in progress?


    # Create helper function to print out attributes
    # in a dict format
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "completed_at": self.completed_at
        }
