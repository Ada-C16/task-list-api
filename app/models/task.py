from flask import app
from app import db

# in each model, write single line w/SQL to 

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200)) 
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """converts task data to dictionary"""

        if self.completed_at == None:
            return {"is_complete": False,
            "id": self.task_id,
            "title": self.title,
            "description": self.description
            }

        else:
            return{
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": True
            }