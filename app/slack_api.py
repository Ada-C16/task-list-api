from slack import WebClient
import os
from dotenv import load_dotenv
from slack.errors import SlackApiError

load_dotenv()
slack_client = WebClient(os.environ.get('SLACK_API_TOKEN'))


def post_msg_slack(msg:str, chan="task-notifications") -> dict:
    message = str(msg)
    response = slack_client.chat_postMessage(
    channel= chan,
    text=message)
    return response