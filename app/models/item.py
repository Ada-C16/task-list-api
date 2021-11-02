from flask_sqlalchemy import Model


class Item(Model):
    @classmethod
    def get_by_id(cls, id):
        try:
            int(id)
        except ValueError:
            400
        return cls.query.get_or_404(id)
