import random
import string

from app.repository.brain.get_default_user_brain import get_user_default_brain


def test_retrieve_all_brains(client, api_key):
    # Making a GET request to the /brains/ endpoint to retrieve all brains for the current user
    response = client.get(
        "/brains/",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    response_data = response.json()
    # Optionally, you can loop through the brains and assert on specific fields in each brain
    for brain in response_data:
        assert "id" in brain
        assert "name" in brain
        assert "rights" in brain
        assert "status" in brain

def test_retrieve_all_public_brains(client, api_key):
    response = client.get(
        "/brains/public",
        headers={"Authorization": "Bearer " + api_key},
    )
    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200
    response_data = response.json()
    for brain in response_data:
        assert "id" in brain
        assert "name" in brain
        assert "description" in brain
        assert "last_update" in brain
        assert "number_of_subscribers" in brain

def test_retrieve_default_brain(client, api_key):
    # Making a GET request to the /brains/default/ endpoint
    response = client.get(
        "/brains/default/",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    default_brain = response.json()
    assert "brain_id" in default_brain
    assert "name" in default_brain


def test_retrieve_one_brain(client, api_key):
    # Making a GET request to the /brains/default/ endpoint
    response = client.get(
        "/brains/default/",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    response_data = response.json()

    # Extract the brain_id from the response
    brain_id = response_data["brain_id"]

    # Making a GET request to the /brains/{brain_id}/ endpoint
    response = client.get(
        f"/brains/{brain_id}/",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    brain = response.json()
    assert "brain_id" in brain
    assert "name" in brain


def test_create_brain(client, api_key):
    # Generate a random name for the brain
    random_brain_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=10)
    )

    # Set up the request payload
    payload = {
        "name": random_brain_name,
        "status": "public",
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 256,
        "openai_api_key": None,
        "prompt_id": None
    }

    # Making a POST request to the /brains/ endpoint
    response = client.post(
        "/brains/",
        json=payload,
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 201

    # Optionally, assert on specific fields in the response
    response_data = response.json()
    # e.g., assert that the response contains a 'brain_id' field
    assert "brain_id" in response_data
    assert "name" in response_data

    # Optionally, assert that the returned 'name' matches the one sent in the request
    assert response_data["name"] == payload["name"]

def test_update_one_brain(client, api_key):
    # Making a GET request to the /brains/default/ endpoint
    response = client.get(
        "/brains/default/",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    response_data = response.json()

    # Extract the brain_id from the response
    brain_id = response_data["brain_id"]

    # Set up the request payload
    payload = {
        "name": "update name",
        "description": "update description",
        "temperature": 0,
        "model": "gpt-3.5-turbo",
        "max_tokens": 256,
        "openai_api_key": None,
        "status": "public",
        "prompt_id": None
    }

    # Making a GET request to the /brains/{brain_id}/ endpoint
    response = client.put(
        f"/brains/{brain_id}/",
        json=payload,
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

def test_set_as_default_brain_endpoint(client, api_key):
    random_brain_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=10)
    )
    # Set up the request payload
    payload = {
        "name": random_brain_name,
        "status": "public",
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 256,
    }

    # Making a POST request to the /brains/ endpoint
    response = client.post(
        "/brains/",
        json=payload,
        headers={"Authorization": "Bearer " + api_key},
    )

    response_data = response.json()

    brain_id = response_data["brain_id"]

    # Make a POST request to set the brain as default for the user
    response = client.post(
        f"/brains/{brain_id}/default",
        headers={"Authorization": "Bearer " + api_key},
    )

    # Assert that the response status code is 200 (HTTP OK)
    assert response.status_code == 200

    # Assert the response message
    assert response.json() == {
        "message": f"Brain {brain_id} has been set as default brain."
    }

    # Check if the brain is now the default for the user

    # Send a request to get user information
    response = client.get("/user", headers={"Authorization": "Bearer " + api_key})
    # Assert that the response contains the expected fields
    user_info = response.json()
    user_id = user_info["id"]

    default_brain = get_user_default_brain(user_id)
    assert default_brain is not None
    assert str(default_brain.brain_id) == str(brain_id)