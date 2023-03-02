from flask import current_app
from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable = False)
    tasks = db.relationship("Task", back_populates="goal", lazy=True)

    # Have to rename? or use the one from Task model?
    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }

    def tasks_to_dict(self):
        task_ids_list = []
        for task in self.tasks:
            task_ids_list.append(task.task_id)
        return {
            "id": self.goal_id,
            "task_ids": task_ids_list
        }