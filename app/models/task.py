from flask import current_app
from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True)
    
    def check_for_completed_task(self):
        if self.completed_at:
            return True
        return False 
    
    def to_dict(self):
        
        return {"id":self.id,
                "title":self.title,
                "description":self.description,
                "is_complete":self.check_for_completed_task()  
        }
