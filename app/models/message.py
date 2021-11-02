from flask import jsonify

class Message():

    @staticmethod
    def success(item, status_code):

        class_name = str(type(item).__name__).lower()

        if class_name=="task" and item.goal_id:
            return jsonify({
                class_name : item.to_dict_with_relationship()
            }), status_code
        
        return jsonify({
                class_name : item.to_dict()
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