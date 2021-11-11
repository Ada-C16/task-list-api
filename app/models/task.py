from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String)
    description=db.Column(db.String)
    completed_at=db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    

    # def task_dict(self):
    #     self.is_complete = False if not self.completed_at else True
    #     return f"{self.task_id} name: {self.title} description: {self.description}"

    def to_json(self):
        return {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": False if self.completed_at == None else True
                }

    def to_dict(self):
    
        task_dict = { 
            "id": self.task_id,
            "title":self.title,
            "description": self.description,
            "is_complete": False if self.completed_at == None else True
        }
        if self.goal_id: 
            task_dict["goal_id"]=self.goal_id
        
        return task_dict