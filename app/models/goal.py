from flask import current_app
from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self, tasks_list=None):
        response_body = {
            "id": self.goal_id,
            "title": self.title
            }

        if tasks_list is not None:
            response_body["tasks"] = tasks_list
        
        return response_body