from flask import current_app
from app import db



class Goal(db.Model):
    # Parent table 
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    # "allows" task to have a relationship with this class
    tasks = db.relationship('Task', backref="goal")
    # back_populates allows the relationship to be bidirectional - we need to do the same on task/child model
    # alternative: set up backref= "parent"  on the parent model only


    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }
