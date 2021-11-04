from flask import current_app
from app import db
from app.models.goal import Goal


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False) # Not sure if I need to specify if these are nullable
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))
    goal = db.relationship("Goal", back_populates="tasks")

    # def __init__(self, dict ={}):
    #     if dict != {}:
    #         self.from_json(dict)

    def to_dict(self):
        response = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
        }
        if self.goal_id:
            response["goal_id"] = self.goal_id
        return response

    # def from_json(self, dict):
    #     self.title = dict["title"]
    #     self.description = dict["description"]
    #     self.completed_at = dict["completed_at"]

        