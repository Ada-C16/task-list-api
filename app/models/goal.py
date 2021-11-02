from flask import current_app
from app import db


class Goal(db.Model):
    __tablename__ = "Goals"
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    tasks = db.relationship('Task', back_populates='goal',lazy=True)

    def to_dict(self):
        return ({"id": self.goal_id, 
                "title": self.title})
