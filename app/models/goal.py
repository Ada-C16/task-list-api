from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    tasks = db.relationship("Task", backref="goal", lazy=True) 

    def to_dict(self, include_tasks=False):
        """converts goal data to dictionary"""
        result = {
            "id": self.goal_id,
            "title": self.title
        }
        if include_tasks:
            result["tasks"]=[task.to_dict() for task in self.tasks]
        return result