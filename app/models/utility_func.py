from flask import current_app
from app import db
from datetime import datetime


def keyError_message():
    return {
        "details": "Invalid data"
        }, 400

def keyError_message_require_all_fields():
    return {
        "message" : "require both title and description"
        }, 400

