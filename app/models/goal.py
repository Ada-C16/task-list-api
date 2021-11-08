from flask import current_app
from app import db
from app.models.task import Task


class Goal(db.Model):
    """This is a model that corresponds to the goal table in the database
    Attrributes:
        - id: generated automatically, int
        - title: must be provided, string
        - tasks: establishes a relationship between Task table and Goal table
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self, include_tasks=False):
        """This is a method that returns a dictionary of the object's attributes"""
        response = {
            "id": self.id,
            "title": self.title,
        }

        if include_tasks:
            response["tasks"] = [task.to_dict() for task in self.tasks]

        return response

    def to_basic_dict(self):
        """This is a method that returns a dictionary of only the goal id and any ids of associated tasks"""
        response = {
            "id": self.id
        }

        if self.tasks:
            response["task_ids"] = [task.id for task in self.tasks]

        return response

    def update(self, goal_dict):
        """This is a method that updates the object's title attribute"""
        self.title = goal_dict["title"]
        return self

    def add_tasks(self, req):
        """This is a method that adds tasks based on their ids to the tasks attribute of the goal"""
        self.tasks = [Task.get_by_id(task_id) for task_id in req["task_ids"]]
        return self

    @classmethod
    def new_from_dict(cls, goal_dict):
        """This is a method to create a new goal object from a dictionary of attributes"""
        return cls(
            title=goal_dict["title"]
        )
