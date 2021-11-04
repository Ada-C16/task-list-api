from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app import db
import datetime


class Task(db.Model):
    __tablename__= 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.goal_id'))
    goal = db.relationship("Goal", back_populates="tasks")

    def task_complete(self):
        if not self.completed_at:
            return False
        return True
        
    def to_dict(self):
        dictionary = {
            "id": self.task_id,
            "title":self.title,
            "description": self.description,
            "is_complete": self.task_complete(),
            }
        if self.goal_id:
            dictionary["goal_id"] = self.goal_id
        return dictionary