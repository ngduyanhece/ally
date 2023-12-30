from typing import Optional

import chainlit as cl

from ally.core.settings import get_supabase_client


def init_chainlit_password_auth():
	@cl.password_auth_callback
	def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
		supabase_client = get_supabase_client()
		response = supabase_client.auth.sign_in_with_password(
			{"email": username, "password": password}
		)
		authentication_dict = response.session.user.identities[0].identity_data

		return cl.AppUser(
			username=authentication_dict.get("email"),
			tags=[str(authentication_dict.get("sub"))]
		)
