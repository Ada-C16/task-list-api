from flask import current_app
from app import db

# task_id: a primary key for each task
# title: text to name the task
# description: text to describe the task
# completed_at: a datetime that has the date that a task is completed on. Can be nullable, and contain a null value. A task with a null value for completed_at has not been completed.

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime,nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)

    def to_dict(self):
        if self.goal_id is None:
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": self.check_for_complete_task(),
            }
        else:

            return{
            
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": self.check_for_complete_task(),
                "goal_id": self.goal_id
                
                }

    def check_for_complete_task(self):
        if self.completed_at:
            return True
        return False

