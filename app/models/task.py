from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = "Tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime,nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('Goals.goal_id'))
    goal = db.relationship("Goal", back_populates = "tasks")

    def to_dict(self):
        return ({"id": self.task_id, 
                "title": self.title,
                "description": self.description,
                "is_complete": self.is_complete_check()})

    def to_dict_with_goal_id(self):
        return ({"id": self.task_id, 
                "goal_id": self.goal_id,
                "title": self.title,
                "description": self.description,
                "is_complete": self.is_complete_check()})

    def is_complete_check(self):
        if not self.completed_at:
            is_complete = False
        else:
             is_complete = True
        return is_complete
        