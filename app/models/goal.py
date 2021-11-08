from flask import current_app
from app import db

#Defining a model for Goal
class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String(200))
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self):
            '''Convert data to a dictionary'''
            goal_dict = {
                "id": self.goal_id,
                "title": self.title,
                
            }
            return goal_dict

    def create_task_list(self):
        task_list = []
        for task in self.tasks:
            task_list.append(task.to_dict())
        return task_list

    def to_dict_and_tasks(self):
        '''Convert data to dictionary including the tasks information'''
        
        goal_dict_task = {
            "id": self.goal_id,
            "title": self.title,
            "tasks": self.create_task_list()}
        return goal_dict_task
