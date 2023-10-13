import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.chat import Chat
from app.models.databases.supabase.supabase import SupabaseDB
from app.models.settings import get_supabase_db
from app.models.user_identity import UserIdentity
from app.models.user_usage import UserUsage
from app.repository.chat.create_chat import CreateChatProperties, create_chat
from app.repository.chat.get_chat_by_id import get_chat_by_id
from app.repository.chat.get_user_chats import get_user_chats
from app.repository.chat.update_chat import (ChatUpdatableProperties,
                                             update_chat)
from app.repository.notification.remove_chat_notifications import \
    remove_chat_notifications

router = APIRouter()

class NullableUUID(UUID):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> UUID | None:
        if v == "":
            return None
        try:
            return UUID(v)
        except ValueError:
            return None
    

def delete_chat_from_db(supabase_db: SupabaseDB, chat_id):
    try:
        supabase_db.delete_chat_history(chat_id)
    except Exception as e:
        print(e)
        pass
    try:
        supabase_db.delete_chat(chat_id)
    except Exception as e:
        print(e)
        pass


def check_user_requests_limit(
    user: UserIdentity,
):
    userDailyUsage = UserUsage(
        id=user.id, email=user.email, openai_api_key=user.openai_api_key
    )

    userSettings = userDailyUsage.get_user_settings()

    date = time.strftime("%Y%m%d")
    userDailyUsage.handle_increment_user_request_count(date)

    if user.openai_api_key is None:
        daily_chat_credit = userSettings.get("daily_chat_credit", 0)
        if int(userDailyUsage.daily_requests_count) >= int(daily_chat_credit):
            raise HTTPException(
                status_code=429,  # pyright: ignore reportPrivateUsage=none
                detail="You have reached the maximum number of requests for today.",  # pyright: ignore reportPrivateUsage=none
            )
    else:
        pass

# get all chats
@router.get("/chats", dependencies=[Depends(AuthBearer())])
async def get_chats(current_user: UserIdentity = Depends(get_current_user)):
    """
    Retrieve all chats for the current user.

    - `current_user`: The current authenticated user.
    - Returns a list of all chats for the user.

    This endpoint retrieves all the chats associated with the current authenticated user. It returns a list of chat objects
    containing the chat ID and chat name for each chat.
    """
    chats = get_user_chats(str(current_user.id))
    return {"chats": chats}

# delete one chat
@router.delete(
    "/chats/{chat_id}", dependencies=[Depends(AuthBearer())]
)
async def delete_chat(chat_id: UUID):
    """
    Delete a specific chat by chat ID.
    """
    supabase_db = get_supabase_db()
    remove_chat_notifications(chat_id)

    delete_chat_from_db(supabase_db=supabase_db, chat_id=chat_id)
    return {"message": f"{chat_id}  has been deleted."}

# update existing chat metadata
@router.put(
    "/chats/{chat_id}/metadata", dependencies=[Depends(AuthBearer())], tags=["Chat"]
)
async def update_chat_metadata_handler(
    chat_data: ChatUpdatableProperties,
    chat_id: UUID,
    current_user: UserIdentity = Depends(get_current_user),
) -> Chat:
    """
    Update chat attributes
    """

    chat = get_chat_by_id(chat_id)  # pyright: ignore reportPrivateUsage=none
    if str(current_user.id) != chat.user_id:
        raise HTTPException(
            status_code=403,  # pyright: ignore reportPrivateUsage=none
            detail="You should be the owner of the chat to update it.",  # pyright: ignore reportPrivateUsage=none
        )
    return update_chat(chat_id=chat_id, chat_data=chat_data)

# create new chat
@router.post("/chats", dependencies=[Depends(AuthBearer())])
async def create_chat_handler(
    chat_data: CreateChatProperties,
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Create a new chat with initial chat messages.
    """

    return create_chat(user_id=current_user.id, chat_data=chat_data)