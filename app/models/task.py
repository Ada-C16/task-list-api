from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))
    goal = db.relationship("Goal", back_populates="tasks",
        single_parent=True,
        cascade="all, delete-orphan")


    def to_dict(self):
        is_complete = False if not self.completed_at else True
        if not self.goal_id:
            return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": is_complete
            }
        return {
                "id": self.task_id,
                "goal_id": self.goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": is_complete
            }
