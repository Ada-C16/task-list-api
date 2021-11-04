from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey(
        "goal.goal_id"), nullable=True)

    def to_dict(self):
        """converts task data to dictionary"""
        result = {"is_complete": True if self.completed_at else False,
                  "title": self.title,
                  "id": self.task_id,
                  "description": self.description
                  }

        if self.goal_id:
            result["goal_id"] = self.goal_id
        return result
