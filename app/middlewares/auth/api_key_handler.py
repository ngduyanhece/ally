from datetime import datetime

from fastapi import HTTPException
from pydantic.v1 import DateError

from app.models.settings import get_supabase_db
from app.modules.api_key.service.api_key_service import APIKeyService
from app.modules.user.entity.user_identity import UserIdentity

api_key_service = APIKeyService()

async def verify_api_key(
	api_key: str,
) -> bool:
	try:
		# Use UTC time to avoid timezone issues
		current_date = datetime.utcnow().date()
		supabase_db = get_supabase_db()
		result = api_key_service.get_active_api_key(api_key)

		if result.data is not None and len(result.data) > 0:
			api_key_creation_date = datetime.strptime(
				result.data[0]["creation_time"], "%Y-%m-%dT%H:%M:%S"
			).date()

			# Check if the API key was created in the month of the current date
			if (api_key_creation_date.month == current_date.month) and (
				api_key_creation_date.year == current_date.year
			):
				return True
		return False
	except DateError:
		return False


async def get_user_from_api_key(
	api_key: str,
) -> UserIdentity:
	supabase_db = get_supabase_db()

	# Lookup the user_id from the api_keys table
	user_id_data = api_key_service.get_user_id_by_api_key(api_key)
	user_email_data = api_key_service.get_user_email_by_api_key(api_key)

	if not user_id_data.data:
		raise HTTPException(status_code=400, detail="Invalid API key.")

	user_id = user_id_data.data[0]["user_id"]
	email = user_email_data.data[0]["email"]

	# Lookup the email from the users table. Todo: remove and use user_id for credentials

	return UserIdentity(email=email, id=user_id)
