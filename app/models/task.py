from flask import current_app
from app import db
from app.models.goal import Goal


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)


    def to_dict(self):

        if self.goal_id == None:
            task_dict = {

            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None,

            }

        else:
            task_dict =  {
            
            "id": self.task_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None,


            }

        return task_dict
        