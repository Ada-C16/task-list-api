from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)  # task name
    description = db.Column(db.String)  # task description
    # null == task is incomplete
    completed_at = db.Column(db.DateTime, nullable=True)
    # wave 6
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")

# helper function

    def to_dict(self):
        task_dict = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        if self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id

        return task_dict
