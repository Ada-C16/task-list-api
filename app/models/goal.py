from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }

    def dict_with_tasks(self):
        tasks = [task.to_dict() for task in self.tasks]
        return {
                "id": self.id,
                "title": self.title,
                "tasks": tasks
                }
    