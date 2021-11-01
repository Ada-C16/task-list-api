from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id'))
    tasks = db.relationship("Task", back_populates = "goal", lazy = True)