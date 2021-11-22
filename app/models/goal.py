from flask import current_app
from app.models.task import Task
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String)
    tasks = db.relationship('Task', backref = 'goal', lazy =True)

    # def to_string(self):
    #     return f"{self.id}: {self.title} Description: {self.description} Completed at: {self.completed_at}"

    def to_dict(self):
        return {
            "id": self.goal_id, 
            "title": self.title
        }
    
    def goal_with_tasks_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title,
            "task_id": self.tasks.id, 
            "title": self.tasks.title,
            "description": self.tasks.description,
            "is_complete": self.tasks.completed_at
        }
    
