from flask import current_app
from app import db



class Goal(db.Model):
    # Parent table 
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    # "allows" task to have a relationship with this class
    tasks = db.relationship('Task', back_populates="goal", lazy=True)
    # back_populates allows the relationship to be bidirectional - we need to do the same on task/child model
    # alternative: set up backref= "parent"  on the parent model only
    # when we say lazy ="true" , it means that it will retrieve the association objects
    #  in a separate query, but not at the time of loading the object, but when the association is first accessed.
    
    def to_dict(self):
        return {
            "id": self.goal_id,
            "title": self.title
        }
