import pytest
from fastapi.testclient import TestClient

from ally.core.settings import settings


@pytest.fixture(scope="session", autouse=True)
def verify_env_variables():
	required_vars = [
		"supabase_url",
		"supabase_service_key",
		"openai_api_key",
		"jwt_secret_key",
		"crawl_depth"
	]
	missing_vars = [var for var in required_vars if not dict(settings)]

	if missing_vars:
		missing_vars_str = ", ".join(missing_vars)
		pytest.fail(f"Required environment variables are missing: {missing_vars_str}")


@pytest.fixture(scope="module")
def client():
	from main import app

	return TestClient(app)


@pytest.fixture(scope="module")
def api_key():
	API_KEY = settings.ci_test_api_key
	if not API_KEY:
		raise ValueError(
			"CI_TEST_API_KEY environment variable not set. Cannot run tests."
		)
	return API_KEY
