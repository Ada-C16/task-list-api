def test_get_tasks_sorted_asc(client, three_tasks):
    # Act
    response = client.get("/tasks?sort=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 2,
            "goal_id" : None,
            "title": "Answer forgotten email 📧",
            "description": "",
            "is_complete": False},
        {
            "id": 3,
            "goal_id" : None,
            "title": "Pay my outstanding tickets 😭",
            "description": "",
            "is_complete": False},
        {
            "id": 1,
            "goal_id" : None,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False}
    ]


def test_get_tasks_sorted_desc(client, three_tasks):
    # Act
    response = client.get("/tasks?sort=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "description": "",
            "id": 1,
            "goal_id" : None,
            "is_complete": False,
            "title": "Water the garden 🌷"},
        {
            "description": "",
            "id": 3,
            "goal_id" : None,
            "is_complete": False,
            "title": "Pay my outstanding tickets 😭"},
        {
            "description": "",
            "id": 2,
            "goal_id" : None,
            "is_complete": False,
            "title": "Answer forgotten email 📧"},
    ]

def test_get_tasks_sorted_neither_asc_nor_desc(client, three_tasks):
    # Act
    response = client.get("/tasks?sort=random_word")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "description": "",
            "id": 1,
            "goal_id" : None,
            "is_complete": False,
            "title": "Water the garden 🌷"},
        {
            "description": "",
            "id": 2,
            "goal_id" : None,
            "is_complete": False,
            "title": "Answer forgotten email 📧"},
        {
            "description": "",
            "id": 3,
            "goal_id" : None,
            "is_complete": False,
            "title": "Pay my outstanding tickets 😭"},
    ]