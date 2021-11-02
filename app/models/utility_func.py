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


def from_str_to_datetime(date_time_str):
    date_time_obj = datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %Z')
    return date_time_obj


