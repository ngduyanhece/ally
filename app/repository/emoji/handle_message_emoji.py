from uuid import UUID

from app.logger import get_logger
from app.models.databases.supabase.emoji import EmojiCode, EmojiOp
from app.models.message_emoji import MessageEmoji
from app.models.settings import get_supabase_db

logger = get_logger(__name__)


def handle_message_emoji(
        message_id: UUID,
        op: EmojiOp,
        emoji: EmojiCode,
        user_id: UUID
) -> MessageEmoji:
    supabase_db = get_supabase_db()

    message_with_emoji = supabase_db.get_emoji_for_message(user_id, message_id)
    existing_emoji = message_with_emoji.emoji == emoji
    logger.info(f"Existing emoji {existing_emoji}")
    if existing_emoji:
        if op == EmojiOp.add:
            logger.info(f"Emoji {emoji} already exists for message {message_id}")
            return message_with_emoji
        elif op == EmojiOp.toggle:
            op = EmojiOp.remove
    else:
        if op == EmojiOp.remove:
            logger.info(f"Emoji {emoji} not found for message {message_id}")
            return message_with_emoji
        elif op == EmojiOp.toggle:
            op = EmojiOp.add

    if op == EmojiOp.add:
        if emoji == EmojiCode.thumbs_up and supabase_db.check_emoji_exist(message_id, user_id, EmojiCode.thumbs_down):
            message_with_emoji = handle_message_emoji(message_id, EmojiOp.remove, EmojiCode.thumbs_down, user_id)
        elif emoji == EmojiCode.thumbs_down and supabase_db.check_emoji_exist(message_id, user_id, EmojiCode.thumbs_up):
            message_with_emoji = handle_message_emoji(message_id, EmojiOp.remove, EmojiCode.thumbs_up, user_id)
        _ = supabase_db.add_emoji(str(message_id), str(user_id), emoji)
        message_with_emoji = supabase_db.get_emoji_for_message(user_id, message_id)
        message_with_emoji.emoji = emoji
    elif op == EmojiOp.remove:
        message_with_emoji = supabase_db.get_emoji_for_message(user_id, message_id)
        if message_with_emoji.emoji and supabase_db.check_emoji_exist(message_id, user_id, message_with_emoji.emoji):
            _ = supabase_db.remove_emoji(str(message_id), str(user_id))
        message_with_emoji = supabase_db.get_emoji_for_message(user_id, message_id)
        message_with_emoji.emoji = emoji   
    else:
        logger.error(f"Unknown emoji operation {op}")
        raise ValueError(f"Unknown emoji operation {op}")
    return message_with_emoji
    
    
