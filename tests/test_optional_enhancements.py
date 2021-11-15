def test_get_tasks_title_query(client, three_tasks):
    # Act
    response = client.get("/tasks?title=water")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 1,
            "title": "Water the garden 🌷",
            "description": "",
            "is_complete": False}
    ]

def test_get_tasks_id_sorted_asc(client, three_tasks):
    # Act
    response = client.get("/tasks?idsort=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "description": "",
            "id": 1,
            "is_complete": False,
            "title": "Water the garden 🌷"},
        {
            "description": "",
            "id": 2,
            "is_complete": False,
            "title": "Answer forgotten email 📧"},
        {
            "description": "",
            "id": 3,
            "is_complete": False,
            "title": "Pay my outstanding tickets 😭"}
    ]

def test_get_tasks_id_sorted_desc(client, three_tasks):
    # Act
    response = client.get("/tasks?idsort=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "description": "",
            "id": 3,
            "is_complete": False,
            "title": "Pay my outstanding tickets 😭"},
        {
            "description": "",
            "id": 2,
            "is_complete": False,
            "title": "Answer forgotten email 📧"},
        {
            "description": "",
            "id": 1,
            "is_complete": False,
            "title": "Water the garden 🌷"}        
    ]

def test_get_goals_sorted_asc(client, three_goals):
    # Act
    response = client.get("/goals?sort=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Build a habit of going outside daily"},
        {
            "id": 3,
            "title": "Relax on a regular basis"},
        {
            "id": 2,
            "title": "Tell the best dad jokes"}
    ]

def test_get_goals_sorted_desc(client, three_goals):
    # Act
    response = client.get("/goals?sort=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 2,
            "title": "Tell the best dad jokes"},
        {
            "id": 3,
            "title": "Relax on a regular basis"},
        {
            "id": 1,
            "title": "Build a habit of going outside daily"}
    ]

def test_get_goals_title_query(client, three_goals):
    # Act
    response = client.get("/goals?title=tell")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 2,
            "title": "Tell the best dad jokes"}
    ]

def test_get_goals_id_sorted_asc(client, three_goals):
    # Act
    response = client.get("/goals?idsort=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Build a habit of going outside daily"},
        {
            "id": 2,
            "title": "Tell the best dad jokes"},
        {
            "id": 3,
            "title": "Relax on a regular basis"}
    ]

def test_get_goals_id_sorted_desc(client, three_goals):
    # Act
    response = client.get("/goals?idsort=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {
            "id": 3,
            "title": "Relax on a regular basis"},
        {
            "id": 2,
            "title": "Tell the best dad jokes"},
        {
            "id": 1,
            "title": "Build a habit of going outside daily"}    
    ]