from flask import current_app
from sqlalchemy.orm import relation
from app import db

class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(200))
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.goal_id'))
    goals = db.relationship("Goal", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
        }

    def to_dict_with_relationship(self):
        return {
            "id": self.task_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
        }

    def to_string_markdown(self):

        completion_status = f"_Completed on {self.completed_at.date()}_." if self.completed_at else "_Incomplete._"

        goal_connection = f"This task belongs to the goal '{self.goals.title}'" if self.goal_id else ""

        return f"*Task:* {self.title.capitalize()}. {completion_status} {goal_connection}"
