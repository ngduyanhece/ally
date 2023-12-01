
from app.models.settings import get_supabase_client
from app.modules.user.entity.user_identity import UserSignInProperties


def sign_in_user(sign_in_data: UserSignInProperties):
    supabase_client = get_supabase_client()
    return supabase_client.auth.sign_in_with_password(dict(sign_in_data))

