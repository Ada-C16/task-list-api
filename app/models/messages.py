from flask import jsonify
from app import db

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

def create_item_slash_command(class_name, data):
    
    item = class_name.__name__.lower()

    title = data.get('text')

    if not title:
        return {
            "response_type" : "ephemeral",
            "text" : f"You forgot to enter the title of your {item}"
        }

    new_item = class_name(title=title)
    db.session.add(new_item)
    db.session.commit()

    return {
        "response_type" : "in_channel",
        "blocks" : [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"New {item} *{title}* has been added.",
                }
            }]
        }

def get_items_slash_command(class_name, data, filter=None):

    item = class_name.__name__.lower()

    if filter == "incomplete":
        items = class_name.query.filter(class_name.completed_at == None)
        qualifier = "incomplete "
    elif filter == "complete":
        items = class_name.query.filter(class_name.completed_at != None)
        qualifier = "completed "
    elif filter and (filter != "incomplete") and (filter != "complete"):
        return {
        "response_type" : "ephemeral",
        "text": "Type 'complete' or 'incomplete' after the /see-tasks command."
        }
    else:
        items = class_name.query.all()
        qualifier = ""

    blocks = [{
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Here are your {qualifier}{item}s",
                }
            }]

    for item in items:
        if item.title:
            item_text = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": item.to_markdown()
                    }
                }
            blocks.append(item_text)

    return {
        "response_type" : "in_channel",
        "blocks": blocks
    }
