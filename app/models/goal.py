from flask import current_app
from app import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }
    
    def update_from_dict(self, data):
        # Loops through attributes provided by users
        for key, value in data.items():
            # Restricts to attributes that are columns
            if key in Goal.__table__.columns.keys():
                setattr(self, key, value)