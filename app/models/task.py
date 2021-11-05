from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.String, nullable = True)
    goal_id_fk = db.Column(db.Integer, db.ForeignKey('goals.goal_id'), nullable=True)
    __tablename__ = 'tasks'

    def to_dict(self):
        if self.goal_id_fk: 
            return({
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at),
                "goal_id": self.goal_id_fk
            })
        else:
            return({
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": bool(self.completed_at)
                
            })

