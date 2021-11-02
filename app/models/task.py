from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
 

    def to_dict(self):
        if self.completed_at == None:
            return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":False,
            }
        else:
            return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":True,
            }

    def to_complete(self):
        return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":True,
            }
    def to_incomplete(self):
        return {
            "id" : self.task_id,
            "title" : self.title,
            "description" : self.description,
            "is_complete":False,
            }


      