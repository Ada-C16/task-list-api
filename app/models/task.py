from flask import current_app
from app import db


class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    fk_goal_id = db.Column(db.Integer, db.ForeignKey('goals.goal_id'), nullable=True)

    def to_dict(self):
        """Defines a series of return options for a dictionary, dependent on if completed and fk_goal_id are null"""
        
        dictionary = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            }

        if not self.completed_at:
            dictionary["is_complete"] = False
            if self.fk_goal_id:
                dictionary["goal_id"] = self.fk_goal_id

        else:
            dictionary["is_complete"] = True
            if self.fk_goal_id:
                dictionary["goal_id"] = self.fk_goal_id
                
        return dictionary
