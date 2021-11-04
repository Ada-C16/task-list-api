

# Create response body for details in error message responses.
def create_details_response(details):
    return {"details": details}

# Create list of tasks.
def list_of_tasks(tasks):
    list_of_tasks = [task.task_body() for task in tasks]
    return list_of_tasks


# Post a notification on Slack when a task has been marked as completed.
def send_slack_notification_of_task_completion(task):
    import requests
    import os
    from dotenv import load_dotenv
    load_dotenv()

    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": os.environ.get("SLACK_API_TOKEN")}
    text = f"Someone just completed the task {task.title}"
    data = {"channel": "task-notifications", "text": text}

    requests.post(url=url, params=data, headers=headers)
