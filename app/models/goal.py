from flask import current_app
from app import db
# from app.models.goal import Goal


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")
    


