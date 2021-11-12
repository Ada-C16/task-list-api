from flask import current_app
from sqlalchemy.orm import lazyload
from app import db
from app.models.goal import Goal


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey(Goal.goal_id), nullable=True)

    def to_dict(self):
        complete = False
        if self.completed_at:
            complete = True
        if self.goal_id:
            return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": complete,
                "goal_id": self.goal_id
            }
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": complete
        }