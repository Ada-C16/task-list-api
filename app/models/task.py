from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    fk_goal_id = db.Column(db.Integer, db.ForeignKey('goals.goal_id'), nullable=True)

    def to_dict(self):
        if not self.completed_at and not self.fk_goal_id:
            return{
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False
            }
        elif self.completed_at and not self.fk_goal_id:
            return{
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True
            }
        elif not self.completed_at and self.fk_goal_id:
            return{
            "id": self.task_id,
            "goal_id": self.fk_goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False
            }
        else:
            return{
                "id": self.task_id,
                "goal_id": self.fk_goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True
            }