from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def to_dict(self, include_tasks=False):
        result = {
            'id': self.goal_id,
            'title': self.title
        }
        if include_tasks:
            result['tasks'] = [task.to_dict() for task in self.tasks]
        return result
    
    def task_ids(self):
        return [task.task_id for task in self.tasks]

goal_schema = {
    "title": "Goal Information",
    "description": "Contains goal related information",
    "required": ["title"],
    "type": ["object"],
    "properties": {
        "title": {
            "type": "string"
        },
        "goal_id": {
            "type": "number"
        }
    }
}