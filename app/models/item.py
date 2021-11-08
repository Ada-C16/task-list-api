from flask_sqlalchemy import Model
from flask import abort


class Item(Model):
    """This is a class to add a custom method to the Model class which Goal and Task inherit from."""
    @classmethod
    def get_by_id(cls, id):
        """This is a method that calls used to get an instance of a model from the database by id
        Parameters:
            - id: a string representing an integer id
        Returns:
            - if id cannot be converted to a valid int:
                - 400 status code, request aborted
            - if id can be converted to a valid int:
                - returns the result of calling cls.query.get_or_404(id)
        """
        try:
            int(id)
        except ValueError:
            abort(400)
        return cls.query.get_or_404(id)
