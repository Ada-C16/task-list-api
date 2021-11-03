from flask import current_app
from app import db



class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task",backref="goal", lazy=True)

    
    def list_of_task_id(self):
        task_ids =[task.id for task in self.tasks]
        return task_ids

    def to_dict(self):
        if self.list_of_task_id():
            
            return {"id":self.id,
                    "title":self.title,
                    "task_ids":self.list_of_task_id() 
                    }
        else:
            return {"id":self.id,
                    "title":self.title,
                    }