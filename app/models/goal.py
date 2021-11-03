from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True) # backref is the name of the attribute in the other model

    def to_dict(self):
        """ Converts the Goal object to a dictionary and adds the tasks if there are some """
        result = {
            "id": self.goal_id,
            "title": self.title
        }
        if len(self.tasks) > 0:
            result["tasks"] = [task.to_dict() for task in self.tasks]
        return result