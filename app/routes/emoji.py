from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.databases.supabase.emoji import RequestEmoji
from app.models.message_emoji import MessageEmoji
from app.models.user_identity import UserIdentity
from app.repository.emoji.handle_message_emoji import handle_message_emoji

router = APIRouter()

@router.post("/emoji", dependencies=[Depends(AuthBearer())])
async def post_emoji_handler(
    emoji: RequestEmoji,
    message_id: UUID = Query(..., description="The ID of the message."),
    current_user: UserIdentity = Depends(get_current_user),
) -> MessageEmoji:
    """
    Toggle, add or remove message emoji.
    """
    return handle_message_emoji(message_id, emoji.op, emoji.emoji, current_user.id)