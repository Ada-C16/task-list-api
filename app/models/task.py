from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable = True)



    # def __init__(self, title, description, completed_at):
    #     self.title = title
    #     self.description= description
    #     self.completed_at = completed_at
    # COLUMNS = ["title", "description", "completed_at"]

    # def task_dict(self):
    #     return {
    #         "id": self.id,
    #         "title": self.title,
    #         "description": self.description
    #     }