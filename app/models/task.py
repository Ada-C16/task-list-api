from app import db

class Task(db.Model):
    __tablename__="tasks"
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """converts task data to dictionary"""
        return {"is_complete": False,
        "id": self.task_id,
        "title": self.title,
        "description": self.description
        }
