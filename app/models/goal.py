from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    # relationship
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def add_tasks_to_goal_dict(self):
        tasks_list = [task.task_id for task in self.tasks]
        return {
            "id": self.goal_id,
            "task_ids": tasks_list
        }
    
    def get_tasks_from_goal_dict(self):
        tasks = [task.to_dict_for_goal() for task in self.tasks]

        return {
            "id": self.goal_id,
            "title": self.title,
            "tasks": tasks
        }