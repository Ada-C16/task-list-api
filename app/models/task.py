from flask import current_app
from app import db
#this is the model for Task which is the schema(structure) for our table
#we want to start creating models so the table shows up in our database, then we can start making requests to populate it


class Task(db.Model): #inheriting from SQLA's model class, turning a basic python class into a SQLA model, Model syntax stays
    task_id = db.Column(db.Integer, primary_key=True) #model creates blueprint for table in our databse
    title = db.Column(db.String) #without db.Column, we would not be able to have these columns in our task table
    description = db.Column(db.String) #when we do db. init we are reading models and from there creating task table
    completed_at = db.Column(db.DateTime, nullable=True) #every column in table requires data type, SQLA takes python and turns it into SQL code
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id')) #creates column in task database.,left side is name of table and right is name of column
    goal = db.relationship("Goal", back_populates="tasks")#lets flask know line 12 has special meaning to write this model

def task_dict(self):
    return f'{self.task_id} title:{self.title} Description: {self.description} Completed_at: {self.completed_at}'
