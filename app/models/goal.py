from flask import current_app
from app import db


class Goal(db.Model):
    __tablename__ = "Goals"
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)

    def to_dict(self):
        return ({"goal": {"id": self.goal_id, 
                "title": self.title}})
