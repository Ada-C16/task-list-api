from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        goal = {
            "id": self.id,
            "title": self.title
        }

        if self.tasks:
            goal["tasks"] = self.tasks

        return goal
