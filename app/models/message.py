from flask import jsonify

class Message():

    @staticmethod
    def success_message(self, status_code):

        class_name = str(type(self).__name__)

        if class_name=="task" and self.goal_id:
            return jsonify({
                class_name : self.to_dict_with_relationship()
            }), status_code
        
        return jsonify({
                class_name : self.to_dict()
            }), status_code

    @staticmethod
    def validate_id(cls, id):

        try:
            int(id) == id

        except ValueError:
            return Message.invalid_data()

        item = cls.query.get(id)

        if not item:
            return "", 404 

    @staticmethod
    def invalid_data():

        return jsonify({ "details" : "Invalid data" }), 400