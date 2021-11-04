from flask import current_app, jsonify
from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    # Determine if is_complete status is true or false depending on if a completed_at time exists.
    def is_complete(self):
        if not self.completed_at:
            is_complete = False
        else:
            is_complete = True

        return is_complete

    # Structure task body for responses.
    def task_body(self):
        task_body = {
        "id": self.task_id,
        "title": self.title,
        "description": self.description,
        "is_complete": self.is_complete()
        }

        if self.goal_id:
            task_body["goal_id"] = self.goal_id
            
        return task_body

    # Create response body for a single task.
    def create_task_response(self):
        return {"task": self.task_body()}