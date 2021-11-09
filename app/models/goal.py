from flask import current_app, jsonify
from app.models.task import Task
from app import db


class Goal(db.Model):
    __tablename__= "goals"
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
        """Defines a method to turn a goal into a dictionary"""
        return{
            "id": self.goal_id,
            "title": self.title
        }

    def to_dict_with_tasks(self, goal_id):
        """Defines  a method to return a goal dictionary with all tasks included"""
        tasks = Task.query.filter_by(fk_goal_id=self.goal_id)
        tasks_list = []
        for task in tasks:
            tasks_list.append(task.to_dict())
        return jsonify({
                "id": self.goal_id,
                "title": self.title,
                "tasks": tasks_list
                })