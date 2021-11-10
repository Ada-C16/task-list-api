from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")

    def to_dict(self):
        if self.completed_at:
            completion_status = True
        else:
            completion_status = False
            
        if self.goal_id:
            return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": completion_status,
            "goal_id": self.goal_id
        }
        else:
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": completion_status,
            }