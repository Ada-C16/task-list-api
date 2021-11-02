from flask import current_app
from app import db


class Goal(db.Model):
    __tablename__ = "goals"
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy=True)


    def convert_a_goal_to_dict(self):
        return {
            "id" : self.goal_id,
            "title" : self.title,   
        }
    
    def goal_id_with_task_list(self, task_ids_list, code):
        return {
        "id" : self.goal_id,
        "task_ids" : task_ids_list
        }, code


        
    def concate_goal_key_to_a_dict_with_return_code(self, code=None):
        return {"goal": self.convert_a_goal_to_dict()}, code
    
