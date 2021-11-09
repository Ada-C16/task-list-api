from flask import current_app
from app import db
from datetime import datetime
from flask import jsonify


class Task(db.Model):
    task_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    completed_at = db.Column(db.DateTime, nullable = True)

    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))
    goal = db.relationship("Goal", back_populates="tasks")

    def is_complete(self):
        return bool(self.completed_at)
    def get_id(self):
        return self.task_id

    def make_dict_response(self, response_code):
        # try: response_body = jsonify({"task" : {
        # "id": self.get_id(),
        # "goal_id": self.goal_id,
        # "title": self.title,
        # "description": self.description,
        # "is_complete": self.is_complete(),
        # }})
        # except AttributeError:
        response_body = jsonify({"task" : {
        "id": self.get_id(),
        "title": self.title,
        "description": self.description,
        "is_complete": self.is_complete(),
        }}), response_code
        return response_body