from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal", lazy=True)

    def to_dict(self):
        tasks = [task.id for task in self.tasks]
        return {
            "id": self.id,
            "title": self.title,
            "task_ids": tasks
        }
    
    def update_from_dict(self, data):
        # Loops through attributes provided by users
        for key, value in data.items():
            # Restricts to attributes that are columns
            if key in Goal.__table__.columns.keys():
                setattr(self, key, value)