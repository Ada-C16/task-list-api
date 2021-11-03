from flask import current_app
from app import db


class Goal(db.Model):
    __tablename__= 'goals'
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    def to_dict_goal(self):
        dictionary = {
            "id": self.goal_id,
            "title":self.title,
            }
        return dictionary



