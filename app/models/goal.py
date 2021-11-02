from flask import current_app
from app import db
from .message import Message


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    __tablename__ = "goals"
    tasks = db.relationship("Task", back_populates="goals", lazy=True)

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def to_dict_with_relationship(self):

        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": [ task.to_dict_with_relationship() for task in self.tasks ]
        }

    @classmethod
    def validate_id(cls, id):
        return Message.validate_id(cls, id)

    def success(self, status_code):
        return Message.success(self, status_code)
