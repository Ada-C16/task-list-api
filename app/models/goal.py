from flask import current_app
from app import db
from datetime import datetime

class Goal(db.Model):
    goal_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    title = db.Column(db.String, nullable = False)
    tasks = db.relationship("Task", back_populates="goal")

    def get_id(self):
        return self.goal