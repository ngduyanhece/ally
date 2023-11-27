from typing import Optional
from uuid import UUID

from app.models import get_supabase_client
from app.modules.user.entity.user_identity import UserIdentity


def create_user_identity(
		id: UUID, openai_api_key: Optional[str], email: Optional[str]
) -> UserIdentity:
	supabase_client = get_supabase_client()

	response = (
		supabase_client.from_("user_identity")
		.insert(
			{
				"user_id": str(id),
				"openai_api_key": openai_api_key,
				"email": email,
			}
		)
		.execute()
	)
	user_identity = response.data[0]
	return UserIdentity(
		id=user_identity["user_id"],
		openai_api_key=user_identity["openai_api_key"],
		email=user_identity["email"],
	)
