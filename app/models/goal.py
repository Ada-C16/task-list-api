from app import db

class Goal(db.Model):
    """"Database model with goal_id, title, and a backref relationship to tasks"""
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    tasks = db.relationship("Task", backref="goal", lazy=True)

    def to_dict(self):
        """Returns a dictionary with Goal ID and title."""
        return({
        "id": self.goal_id, 
        "title": self.title
        }) 