from app import db
from flask import request, current_app


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", backref="goal")

    def create_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title,
        }

    @classmethod
    def goal_arguments(cls, title_from_url):
        if title_from_url:
            goals = Goal.query.filter_by(title=title_from_url).all()
            if not goals:
                goals = Goal.query.filter(Goal.title.contains(title_from_url))
        else:
            goals = Goal.query.all()
        return goals
