from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self):
        response = {
            "id": self.id,
            "title": self.title,
        }

        if self.tasks:
            response["tasks"] = [task.to_dict() for task in self.tasks]

        return response

    def to_basic_dict(self):
        response = {
            "id": self.id
        }

        if self.tasks:
            response["task_ids"] = [task.id for task in self.tasks]

        return response
