from flask import current_app
from app import db
import slack
import os
from dotenv import load_dotenv
from slack import WebClient
from slack.errors import SlackApiError



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable = True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))
    
    def check_for_completed_task(self):
        if self.completed_at:
            return True
        return False 
    
    def to_dict(self):
        if self.goal_id is None:
        
            return {"id":self.id,
                    "title":self.title,
                    "description":self.description,
                    "is_complete":self.check_for_completed_task()
            }
        else:
            return {"id":self.id,
                    "title":self.title,
                    "description":self.description,
                    "is_complete":self.check_for_completed_task(),
                    "goal_id": self.goal_id  
            }
    def slack_notification(self):
        if self.completed_at:
            load_dotenv()
            slack_token = os.environ["SLACK_TOKENS"]
            client = WebClient(token=slack_token)
            try:
                response = client.chat_postMessage(
                    channel ="CNEEJDLAW",
                    text = "Task completed"
                )
            except SlackApiError as e:
                return jsonify({"Error": "chanel not found"})
