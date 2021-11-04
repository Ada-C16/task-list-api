from flask import Blueprint, jsonify,request, make_response
import slack
import os
from dotenv import load_dotenv
import logging
# logging.basicConfig(level=logging.DEBUG)
from slack import WebClient
from slack.errors import SlackApiError

# client = slack.Webclient(token=os.environ['SLACK_TOKENS'])
# client.chat_postmessage(channel=yourchannel, text="Task completed")

def slack_notification():
    slack_token = os.environ["SLACK_TOKENS"]
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(
            channel ="CNEEJDLAW",
            text = "Task completed"
        )
    except SlackApiError as e:
        return jsonify({"Error": "chanel not found"})