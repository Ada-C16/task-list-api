from flask import current_app
from app import db
from app.routes.route_utils import is_valid_int


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"))
    goal = db.relationship("Goal", back_populates="tasks")

    def to_dict(self):
        is_complete = False if not self.completed_at else True

        response = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": is_complete,
        }

        if self.goal:
            response["goal_id"] = self.goal_id

        return response

    def update(self, task_dict):
        self.title = task_dict["title"]
        self.description = task_dict["description"]

        if "completed_at" in task_dict:
            self.completed_at = task_dict["completed_at"]

        return self

    @classmethod
    def new_from_dict(cls, task_dict):
        return cls(
            title=task_dict["title"],
            description=task_dict["description"],
            completed_at=task_dict["completed_at"]
        )

    @classmethod
    def get_by_id(cls, id):
        """Grab one task from the database by id and return it"""
        is_valid_int(id)
        return cls.query.get_or_404(id)
