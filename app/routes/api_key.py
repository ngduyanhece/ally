from secrets import token_hex
from typing import List
from uuid import uuid4

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.settings import get_supabase_db
from app.models.user_identity import UserIdentity

logger = get_logger(__name__)


class ApiKeyInfo(BaseModel):
    key_id: str
    creation_time: str

class ApiKey(BaseModel):
    api_key: str
    key_id: str


router = APIRouter()

@router.post(
    "/api-keys",
    response_model=ApiKey,
    dependencies=[Depends(AuthBearer())]
)
async def create_api_key(
    current_user: UserIdentity = Depends(get_current_user)
):
    """
    Create new API key for the current user.

    - `current_user`: The current authenticated user.
    - Returns the newly created API key.

    This endpoint generates a new API key for the current user. The API key is stored in the database and associated with
    the user. It returns the newly created API key.
    """

    new_key_id = uuid4()
    new_api_key = token_hex(16)
    api_key_inserted = False
    supabase_db = get_supabase_db()

    while not api_key_inserted:
        try:
            # Attempt to insert new API key into database
            supabase_db.create_api_key(new_key_id, new_api_key, current_user.id, current_user.email)
            api_key_inserted = True

        except UniqueViolationError:
            # Generate a new API key if the current one is already in use
            new_api_key = token_hex(16)
        except Exception as e:
            logger.error(f"Error creating new API key: {e}")
            return {"api_key": "Error creating new API key."}
    logger.info(f"Created new API key for user {current_user.email}.")

    return {"api_key": new_api_key, "key_id": str(new_key_id)}


@router.delete(
    "/api-keys/{key_id}", dependencies=[Depends(AuthBearer())]
)
async def delete_api_key(
    key_id: str, current_user: UserIdentity = Depends(get_current_user)
):
    """
    Delete (deactivate) an API key for the current user.

    - `key_id`: The ID of the API key to delete.

    This endpoint deactivates and deletes the specified API key associated with the current user. The API key is marked
    as inactive in the database.

    """
    supabase_db = get_supabase_db()
    supabase_db.delete_api_key(key_id, current_user.id)

    return {"message": "API key deleted."}

@router.get(
    "/api-keys",
    response_model=List[ApiKeyInfo],
    dependencies=[Depends(AuthBearer())]
)
async def get_api_keys(current_user: UserIdentity = Depends(get_current_user)):
    """
    Get all active API keys for the current user.

    - `current_user`: The current authenticated user.
    - Returns a list of active API keys with their IDs and creation times.

    This endpoint retrieves all the active API keys associated with the current user. It returns a list of API key objects
    containing the key ID and creation time for each API key.
    """
    supabase_db = get_supabase_db()
    response = supabase_db.get_user_api_keys(current_user.id)
    return response
