from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")
    
    

    # def to_string(self):
    #     return f"{self.id}: {self.title} {self.description} {self.completed_at}"
