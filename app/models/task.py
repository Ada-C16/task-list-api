from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey(
        'goal.goal_id'), nullable=True)
    goal = db.relationship('Goal', back_populates='tasks')

    def check_completed_at(self):
        if self.completed_at is not db.DateTime:
            return "Invalid completed_at entry."

    def task_dict(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False if self.completed_at is None else True}

    def task_dict_with_goal(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False if self.completed_at is None else True,
            "goal_id": self.goal_id
        }
