from app.models.goal import Goal
from app.models.task import Task 

def test_get_tasks_filtered_by_title(client, three_tasks):
    # Act
    response = client.get("/tasks?title=Answer forgotten email 📧")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False
        }
    ]


def test_get_ids_sorted_asc(client, three_tasks):
    # Act
    response = client.get("/tasks?sort_id=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False},
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False},
        {
            "id": 3,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False},
        
    ]



def test_get_ids_sorted_desc(client, three_tasks):
    # Act
    response = client.get("/tasks?sort_id=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [

        {
            "id": 3,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False},
        
        {
            "id": 2,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False},
        
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False},
    ]


def test_get_tasks_filtered_by_title(client, three_goals):
    # Act
    response = client.get("/goals?title=Get internship at Google")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 3,
            "title":"Get internship at Google"
        }
    ]
