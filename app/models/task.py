from flask import current_app
from app import db
from app.models.goal import Goal


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, default=None, nullable=True)
    is_complete = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)

    def to_dict(self):
        if not self.goal_id:
            return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": self.is_complete
            }

        return {
            "id": self.task_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.is_complete
        }