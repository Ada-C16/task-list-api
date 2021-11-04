from app import db

class Goal(db.Model):
    __tablename__="goals"
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))

    def to_dict(self):
        """converts goal data to dictionary"""
        return {
        "id": self.goal_id,
        "title": self.title
        }
