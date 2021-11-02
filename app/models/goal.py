from flask import current_app
from app.models.task import Task
from app import db


class Goal(db.Model):
    __tablename__= "goals"
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
        return{
            "id": self.goal_id,
            "title": self.title
        }

    def to_dict_with_tasks(self, goal_id):
        tasks = Task.query.filter_by(fk_goal_id=f"{goal_id}")
        tasks_list = []
        for task in tasks:
            tasks_list.append(task.to_dict())
        return {
                "id": self.goal_id,
                "title": self.title,
                "tasks": tasks_list
                }