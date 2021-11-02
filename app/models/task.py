# from flask import current_app
# from app import db


# class Task(db.Model):
#     task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title=db.Column(db.String(200))
#     description=db.Column(db.String(200))
#     comleted_at=db.Column(db.DateTime, nullable=True)#default=None

#     def to_dict(self):
#         return{
#             "id":self.task_id,
#             "title": self.title,
#             "description": self.description,
#             "is_complete": True if self.completed_at else False
#         }
###########below is my first attempt
from flask import current_app
from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(50))
    description=db.Column(db.String(200))
    completed_at=db.Column(db.DateTime, nullable=True)#default=None
    # expected_to_be_fun=db.Column(db.String)
    
    def to_dict(self):
        if self.completed_at == None:
            return {
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": False
            #IF NOT COMPLETE AT IS NULL OR POPULATED
        }

        else:
            return{
            "id":self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": True
        }
        
        # return task_dict

