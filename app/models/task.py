from flask import current_app
from app import db
# from app.models.goal import Goal

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")


    def to_json(self):
        return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at)
        }

    def to_json_task(self):
        return {
                "id": self.id,
                "goal_id": self.goal.goal_id,
                # "goal_id": Goal(self.goal_id, self.title).goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at)
        }

