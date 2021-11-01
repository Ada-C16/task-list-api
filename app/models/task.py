from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id =  db.Column(db.Integer, db.ForeignKey('goals.goal_id'), nullable=True)


    def convert_a_task_to_dict(self, goal_id=None):
        res = {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete" : True if self.completed_at else False
        }

        if goal_id:
            res["goal_id"] = self.goal_id
        return res




