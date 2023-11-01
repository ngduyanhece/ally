from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.databases.supabase.meta_brains import (
    CreatedMetaBrainOutput, CreateMetaBrainProperties,
    MetaBrainUpdatableProperties)
from app.models.meta_brain_entity import (MetaBrainEntity,
                                          MinimalMetaBrainEntity,
                                          PublicMetaBrain)
from app.models.user_identity import UserIdentity
from app.models.user_usage import UserUsage
from app.repository.brain.set_as_default_brain_for_user import \
    set_as_default_brain_for_user
from app.repository.meta_brain.create_meta_brain import create_meta_brain
from app.repository.meta_brain.create_meta_brain_user import \
    create_meta_brain_user
from app.repository.meta_brain.delete_meta_brain_user import \
    delete_meta_brain_user
from app.repository.meta_brain.get_default_user_meta_brain import \
    get_user_default_meta_brain
from app.repository.meta_brain.get_default_user_meta_brain_or_create_new import \
    get_default_user_brain_or_create_new
from app.repository.meta_brain.get_meta_brain_details import \
    get_meta_brain_details
from app.repository.meta_brain.get_public_meta_brains import \
    get_public_meta_brains
from app.repository.meta_brain.get_user_meta_brains import get_user_meta_brains
from app.repository.meta_brain.update_meta_brain import update_meta_brain_by_id
from app.routes.authorizations.meta_brain_authorization import \
    has_meta_brain_authorization
from app.routes.authorizations.types import RoleEnum

logger = get_logger(__name__)
router = APIRouter()

# get all meta brains
@router.get("/meta_brains/",
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(AuthBearer())])
async def get_all_meta_brains_endpoint(
    current_user: UserIdentity = Depends(get_current_user),
) -> list[MinimalMetaBrainEntity]:
    """
    Retrieve all meta brains for the current user.

    - `current_user`: The current authenticated user.
    - Returns a list of all meta brains registered for the user.

    This endpoint retrieves all the meta brains associated with the current authenticated user
    """
    meta_brains = get_user_meta_brains(current_user.id)
    return meta_brains

@router.get(
    "/meta_brains/public",
    status_code=status.HTTP_200_OK, 
    dependencies=[Depends(AuthBearer())])
async def get_all_public_meta_brains_endpoint() -> list[PublicMetaBrain]:
    """
    Retrieve all ally public meta brains
    """
    return get_public_meta_brains()

# get default meta brain
@router.get(
    "/meta_brains/default/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AuthBearer())])
async def get_default_meta_brain_endpoint(
    current_user: UserIdentity = Depends(get_current_user),
) -> MetaBrainEntity:
    """
    Retrieve the default meta brain for the current user. If the user doesnt have one, it creates one.

    - `current_user`: The current authenticated user.
    - Returns the default meta brain for the user.

    This endpoint retrieves the default meta brain associated with the current authenticated user.
    The default meta brain is defined as the meta brain marked as default in the meta_brains_users table.
    """

    meta_brain = get_default_user_brain_or_create_new(current_user)
    return meta_brain

@router.get(
    "/meta_brains/{meta_brain_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AuthBearer()), Depends(has_meta_brain_authorization())]
)
async def get_meta_brain_endpoint(
    meta_brain_id: UUID,
) -> MetaBrainEntity | None:
    """
    Retrieve details of a specific meta brain by meta brain ID.

    - `meta_brain_id`: The ID of the meta brain to retrieve details for.
    - Returns the meta brain ID and its history.
    - Raises a 404 error if the meta brain is not found.

    This endpoint retrieves the details of a specific meta brain identified by the provided meta brain ID
    """

    meta_brain_details = get_meta_brain_details(meta_brain_id)
    if meta_brain_details is None:
        raise HTTPException(
            status_code=404,
            detail="Meta Brain details not found",
        )

    return meta_brain_details

# create new meta brain
@router.post("/meta_brains/",
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(AuthBearer())])
async def create_meta_brain_endpoint(
    meta_brain: CreateMetaBrainProperties,
    current_user: UserIdentity = Depends(get_current_user),
) -> CreatedMetaBrainOutput:
    """
    Create a new meta brain with given
        name
        status
        model
        max_tokens
        temperature
    In the meta brains table & in the brains_users table and put the creator user as 'Owner'
    """

    user_meta_brains = get_user_meta_brains(current_user.id)
    userDailyUsage = UserUsage(
        id=current_user.id,
        email=current_user.email,
        openai_api_key=current_user.openai_api_key,
    )
    userSettings = userDailyUsage.get_user_settings()

    if len(user_meta_brains) >= userSettings.get("max_meta_brains", 2):
        raise HTTPException(
            status_code=429,
            detail=f"Maximum number of meta brains reached ({userSettings.get('max_meta_brains', 2)}).",
        )

    new_meta_brain = create_meta_brain(
        meta_brain,
    )
    default_meta_brain = get_user_default_meta_brain(current_user.id)
    if default_meta_brain:
        logger.info(f"Default meta brain already exists for user {current_user.id}")
        create_meta_brain_user(
            user_id=current_user.id,
            meta_brain_id=new_meta_brain.meta_brain_id,
            rights=RoleEnum.Owner,
            is_default_meta_brain=False,
        )
    else:
        logger.info(
            f"Default meta brain does not exist for user {current_user.id}. It will be created."
        )
        create_meta_brain_user(
            user_id=current_user.id,
            meta_brain_id=new_meta_brain.meta_brain_id,
            rights=RoleEnum.Owner,
            is_default_meta_brain=True,
        )

    return {
        "meta_brain_id": new_meta_brain.meta_brain_id,
        "name": new_meta_brain.name,
        "rights": "Owner",
    }

# update existing meta brain
@router.put(
    "/meta_brains/{meta_brain_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            AuthBearer(),
        ),
        Depends(has_meta_brain_authorization([RoleEnum.Editor, RoleEnum.Owner])),
    ],
)
async def update_meta_brain_endpoint(
    meta_brain_id: UUID,
    meta_brain_to_update: MetaBrainUpdatableProperties,
) -> MetaBrainEntity | None:
    """
    Update an existing brain with new brain configuration
    """

    existing_meta_brain = get_meta_brain_details(meta_brain_id)
    if existing_meta_brain is None:
        raise HTTPException(
            status_code=404,
            detail="Meta Brain not found",
        )
    
    if meta_brain_to_update.status == "private" and existing_meta_brain.status == "public":
        delete_meta_brain_user(meta_brain_id)

    update_meta_brain = update_meta_brain_by_id(meta_brain_id, meta_brain_to_update)

    return update_meta_brain

# set as default meta brain
@router.post(
    "/meta_brains/{meta_brain_id}/default",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            AuthBearer(),
        ),
        Depends(has_meta_brain_authorization()),
    ],
)
async def set_as_default_meta_brain_endpoint(
    meta_brain_id: UUID,
    user: UserIdentity = Depends(get_current_user),
):
    """
    Set a brain as default for the current user.
    """

    set_as_default_brain_for_user(user.id, meta_brain_id)

    return {"message": f"Meta Brain {meta_brain_id} has been set as default meta brain."}
