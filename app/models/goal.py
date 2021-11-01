from flask import current_app
from app import db


class Goal(db.Model):
    __tablename__ = "goals"
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy=True)


    def convert_a_goal_to_dict(self):
        return {
            "id" : self.goal_id,
            "title" : self.title,   
        }