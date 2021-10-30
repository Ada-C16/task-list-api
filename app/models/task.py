from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String)
    description=db.Column(db.String)
    completed_at=db.Column(db.DateTime, nullable=True)

    # def task_dict(self):
    #     self.is_complete = False if not self.completed_at else True
    #     return f"{self.task_id} name: {self.title} description: {self.description}"

    def to_json(self):
        return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": False if self.completed_at == None else True
                }