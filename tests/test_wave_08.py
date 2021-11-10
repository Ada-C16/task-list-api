# Additional tests
import datetime
from app.models.task import Task

def test_bad_date_input_create_new_task(client):
    # Act
    response = client.post("/tasks", json={
        "title": "A Brand New Task",
        "description": "Test Description",
        "completed_at": "Friday"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "error" in response_body
    assert response_body == {
        "error": "Invalid data type in request body"
        }
    assert Task.query.all() == []

def test_bad_date_input_updating_task(client, completed_task_old):
    # Act
    response = client.put("/tasks/1", json={
        "completed_at": 'Feb 2015'
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "error" in response_body
    assert response_body == {
        "error": "Invalid data type in request body"
        }
    task = Task.query.get(1)
    assert task.title == "Make lentil soup"
    assert task.description == "Prepare Thursday night dinner"
    assert task.completed_at == datetime.datetime(2021, 10, 24, 18, 7, 55)