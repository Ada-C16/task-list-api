import pytest

def test_get_goals_no_saved_goals(client):
    # Act
    response = client.get("/goals")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == []


def test_get_goals_one_saved_goal(client, one_goal):
    # Act
    response = client.get("/goals")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 1,
            "title": "Build a habit of going outside daily"
        }
    ]


def test_get_goal(client, one_goal):
    # Act
    response = client.get("/goals/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert "goal" in response_body
    assert response_body == {
        "goal": {
            "id": 1,
            "title": "Build a habit of going outside daily"
        }
    }


def test_get_goal_not_found(client):
    # Act
    response = client.get("/goals/1")
    response_body = response.get_json()

    # Assert
    # ---- Complete Test ----
    # assertion 1 goes here
    assert response.status_code == 404
    # assertion 2 goes here
    assert response_body == None
    # ---- Complete Test ----

def test_create_goal(client):
    # Act
    response = client.post("/goals", json={
        "title": "My New Goal"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 201
    assert "goal" in response_body
    assert response_body == {
        "goal": {
            "id": 1,
            "title": "My New Goal"
        }
    }


def test_update_goal(client, one_goal):
    # Act
    # ---- Complete Act Here ----
    response = client.put("goals/1", json={
        "title": "Make up my bed first thing in the morning."})
    response_body = response.get_json()

    # Assert
    # ---- Complete Assertions Here ----
    # assertion 1 goes here
    assert response.status_code == 200
    # assertion 2 goes here
    assert len(response_body) == 1
    # assertion 3 goes here
    assert response_body == {
        "goal": {
            "id": 1,
            "title": "Make up my bed first thing in the morning."
        }
    }
    # ---- Complete Assertions Here ----


def test_update_goal_not_found(client):
    # Act
    # ---- Complete Act Here ----
    response = client.put("goals/1")
    response_body = response.get_json()

    # Assert
    # ---- Complete Assertions Here ----
    # assertion 1 goes here
    assert response.status_code == 404
    # assertion 2 goes here
    assert response_body == None
    # ---- Complete Assertions Here ----


def test_delete_goal(client, one_goal):
    # Act
    response = client.delete("/goals/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert "details" in response_body
    assert response_body == {
        "details": 'Goal 1 "Build a habit of going outside daily" successfully deleted'
    }

    # Check that the goal was deleted
    response = client.get("/goals/1")
    assert response.status_code == 404


def test_delete_goal_not_found(client):
    # Act
    # ---- Complete Act Here ----
    response = client.delete("/goals/1")
    response_body = response.get_json()

    # Assert
    # ---- Complete Assertions Here ----
    # assertion 1 goes here
    assert response.status_code == 404
    # assertion 2 goes here
    assert response_body == None
    # ---- Complete Assertions Here ----


def test_create_goal_missing_title(client):
    # Act
    response = client.post("/goals", json={})
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert response_body == {
        "details": "Invalid data"
    }
