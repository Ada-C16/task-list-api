from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False )
    completed_at = db.Column(db.DateTime, nullable=True)
    fk_goal_id = db.Column(db.Integer,db.ForeignKey('goal.goal_id'), nullable=True)

    def to_dict(self):
        # if not self.completed_at and not self.fk_goal_id:
        task_dict= {
            "id":self.task_id,
            "title" : self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)}
        if self.fk_goal_id is not None:
            task_dict["goal_id"]=self.fk_goal_id
        return task_dict
        # elif self.completed_at and not self.fk_goal_id:
        #     return{
        #         "id":self.task_id,
        #         "title" : self.title,
        #         "description": self.description,
        #         "is_complete": bool(self.completed_at)
        #     }
        # # elif not self.completed_at and self.fk_goal_id:
        # # else:
        #     return {
        #         "id":self.task_id,
        #         "goal_id":self.fk_goal_id,
        #         "title" : self.title,
        #         "description": self.description,
        #         "is_complete": bool(self.completed_at)
        #     }