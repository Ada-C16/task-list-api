from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")
    # completed_at = db.Column(db.DateTime, nullable=True, default=None)
    # # null in postman
    # is_complete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        if self.completed_at:
            is_complete = True
        else:
            is_complete = False
        if self.goal_id:
            return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": is_complete,
            "goal_id": self.goal_id
        }
        else:
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "is_complete": is_complete,
            }
    
    # def to_dict_with_goal_id(self):
    #     if self.completed_at:
    #         is_complete = True
    #     else:
    #         is_complete = False
    #     return {
    #         "id": self.id,
    #         "title": self.title,
    #         "description": self.description,
    #         "is_complete": is_complete,
    #         "goal_id": self.goal_id
    #     }