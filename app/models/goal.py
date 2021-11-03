from flask import current_app
from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    __tablename__ = "goals"
    tasks = db.relationship("Task", back_populates="goals", lazy=True)

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def to_dict_with_relationship(self):

        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": [ task.to_dict_with_relationship() for task in self.tasks ]
        }

    def to_markdown(self):

        goal_string = f"*Goal:* {self.title.capitalize()}." 

        if self.tasks:
            goal_string += """
            *Related tasks*:"""
            for task in self.tasks:
                goal_string += """
                - """
                goal_string += task.title

        return goal_string
