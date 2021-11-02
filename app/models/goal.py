from flask import current_app
from sqlalchemy.orm import relationship
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = relationship("Task", lazy=False)
