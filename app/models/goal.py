from flask import current_app
from sqlalchemy.orm import backref
from app import db
"""
In a one to many relationship, the table on the many side of the relationship, called the child table, 
contains a field which references the primary key of the table on the one side of the relationship, called the parent. 
"""

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="goal", lazy = True)