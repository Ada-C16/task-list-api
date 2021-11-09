from flask import current_app
from app import db
from datetime import datetime
from flask import jsonify

class Goal(db.Model):
    goal_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    title = db.Column(db.String, nullable = False)
    tasks = db.relationship("Task", back_populates="goal")

    def get_id(self):
        return self.goal_id
    def make_dict_response(self, response_code):
        response_body = jsonify({"goal" : {
        "id": self.get_id(),
        "title": self.title,
        }}), response_code
        return response_body