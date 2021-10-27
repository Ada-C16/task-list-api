from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    def create_dict(self):
        complete_status = False
        if self.completed_at:
            complete_status = True

        return {"task":
                    {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": complete_status,
        }}