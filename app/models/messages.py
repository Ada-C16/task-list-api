from flask import jsonify

def success_message(db_item, status_code):

    class_name = db_item.__class__.__name__.lower()

    if class_name=="task" and db_item.goal_id:
        return jsonify({
            class_name : db_item.to_dict_with_relationship()
        }), status_code
    
    return jsonify({
            class_name : db_item.to_dict()
        }), status_code

def invalid_data_message():
    return jsonify({ "details" : "Invalid data" }), 400

def validate_id(Item, id):

    try:
        int(id) == id

    except ValueError:
        return invalid_data_message()

    item = Item.query.get(id)

    if not item:
        return "", 404
