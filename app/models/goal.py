from flask import app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(100))

    # tasks = db.relationship("Task", backref="task", lazy = True)

    # def to_json(self):
    #     return{
    #         "id": self.goal_id, 
    #         "title": self.title,
    #     }
