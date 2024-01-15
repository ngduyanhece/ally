
from ally.modules.api_key.repository.api_keys import ApiKeys

APIKeyService = ApiKeys()


def test_create_and_delete_api_key(client, api_key):
	# First, let's create an API key
	response = client.post(
		"/api-keys",
		headers={
			"Authorization": "Bearer " + api_key,
		},
	)
	assert response.status_code == 201
	api_key_info = response.json()
	assert "api_key" in api_key_info

	# Extract the created api_key from the response
	api_key = api_key_info["api_key"]

	# Now, let's verify the API key
	verify_response = client.get(
		"/api-keys",
		headers={
			"Authorization": f"Bearer {api_key}",
		},
	)
	assert verify_response.status_code == 200

	# Now, let's delete the API key
	assert "id" in api_key_info
	key_id = api_key_info["id"]

	delete_response = client.delete(
		f"/api-keys/{key_id}", headers={"Authorization": f"Bearer {api_key}"}
	)
	assert delete_response.status_code == 200
	assert delete_response.json() == {"message": "API key deleted."}


def test_get_user_from_api_key(client, api_key):
	# Call the function with a test API key
	user = APIKeyService.get_user_id_by_api_key(api_key)

	# Use an assertion to check the returned user
	assert user is not None, "User should not be None"


def test_verify_api_key(client, api_key):
	# Call the function with a test API key
	user = APIKeyService.get_user_id_by_api_key(api_key).data[0]["user_id"]

	user_api_keys = APIKeyService.get_user_api_keys(user)
	# Use an assertion to check the returned user
	assert user_api_keys is not None, "User should not be None"
	assert len(user_api_keys) > 0, "User should have at least one API key"
