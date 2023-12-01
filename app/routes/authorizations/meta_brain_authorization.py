from typing import List, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.auth.auth_bearer import get_current_user
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.meta_brain.get_meta_brain_details import \
    get_meta_brain_details
from app.repository.meta_brain.get_meta_brain_for_user import \
    get_meta_brain_for_user
from app.routes.authorizations.types import RoleEnum


def has_meta_brain_authorization(
    required_roles: Optional[Union[RoleEnum, List[RoleEnum]]] = RoleEnum.Owner
):
    """
    Decorator to check if the user has the required role(s) for the meta brain
    param: required_roles: The role(s) required to access the meta brain
    return: A wrapper function that checks the authorization
    """

    async def wrapper(
        meta_brain_id: UUID, current_user: UserIdentity = Depends(get_current_user)
    ):
        nonlocal required_roles
        if isinstance(required_roles, str):
            required_roles = [required_roles]  # Convert single role to a list
        validate_meta_brain_authorization(
            meta_brain_id=meta_brain_id, user_id=current_user.id, required_roles=required_roles
        )

    return wrapper


def validate_meta_brain_authorization(
    meta_brain_id: UUID,
    user_id: UUID,
    required_roles: Optional[Union[RoleEnum, List[RoleEnum]]] = RoleEnum.Owner,
):
    """
    Function to check if the user has the required role(s) for the brain
    param: brain_id: The id of the brain
    param: user_id: The id of the user
    param: required_roles: The role(s) required to access the brain
    return: None
    """

    meta_brain = get_meta_brain_details(meta_brain_id)

    if meta_brain and meta_brain.status == "public":
        return

    if required_roles is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required role",
        )

    user_meta_brain = get_meta_brain_for_user(user_id, meta_brain_id)
    if user_meta_brain is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for meta this brain",
        )

    # Convert single role to a list to handle both cases
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    # Check if the user has at least one of the required roles
    if user_meta_brain.rights not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the required role(s) for this meta brain",
        )
