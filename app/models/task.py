from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at= db.Column(db.DateTime, nullable=True)
    # one goal has many tasks - this model is the child model
    # we place the foreign key on the child model refering the parent
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")


    def to_dict(self):

        value = False
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else value
        }

    def to_dict_goal_task(self):

        value = False
        return {
            "id": self.task_id,
            "goal_id":self.goal_id if self.goal_id else None,
            "title": self.title,
            "description": self.description,
            "is_complete": True if self.completed_at else value
        }