from app import db

#child class
#tasks belongs to one goal 
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))

    completed_at = db.Column(db.DateTime, nullable=True)
