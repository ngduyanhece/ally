from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.brains import Brain
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.files.delete_file import delete_file_from_storage
from app.repository.files.generate_file_signed_url import \
    generate_file_signed_url
from app.repository.knowledge.get_all_knowledge import get_all_knowledge
from app.repository.knowledge.get_knowledge import get_knowledge
from app.repository.knowledge.remove_knowledge import remove_knowledge
from app.routes.authorizations.brain_authorization import (
    has_brain_authorization, validate_brain_authorization)
from app.routes.authorizations.types import RoleEnum

router = APIRouter()
logger = get_logger(__name__)

@router.get(
    "/knowledge", dependencies=[Depends(AuthBearer())]
)
async def list_knowledge_in_brain_endpoint(
    brain_id: UUID = Query(..., description="The ID of the brain"),
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Retrieve and list all the knowledge in a brain.
    """

    validate_brain_authorization(brain_id=brain_id, user_id=current_user.id)

    knowledges = get_all_knowledge(brain_id)
    # logger.info("List of knowledge from knowledge table", knowledges)

    return {"knowledges": knowledges}


@router.delete(
    "/knowledge/{knowledge_id}",
    dependencies=[
        Depends(AuthBearer()),
        Depends(has_brain_authorization(RoleEnum.Owner)),
    ],
    tags=["Knowledge"],
)
async def delete_endpoint(
    knowledge_id: UUID,
    current_user: UserIdentity = Depends(get_current_user),
    brain_id: UUID = Query(..., description="The ID of the brain"),
):
    """
    Delete a specific knowledge from a brain.
    """

    validate_brain_authorization(brain_id=brain_id, user_id=current_user.id)

    brain = Brain(id=brain_id)

    knowledge = get_knowledge(knowledge_id)
    file_name = knowledge.file_name if knowledge.file_name else knowledge.url
    remove_knowledge(knowledge_id)

    if knowledge.file_name:
        delete_file_from_storage(f"{brain_id}/{knowledge.file_name}")
        brain.delete_file_from_brain(knowledge.file_name)
    elif knowledge.url:
        brain.delete_file_from_brain(knowledge.url)

    return {
        "message": f"{file_name} of brain {brain_id} has been deleted by user {current_user.email}."
    }

@router.get(
    "/knowledge/{knowledge_id}/signed_download_url",
    dependencies=[Depends(AuthBearer())],
    tags=["Knowledge"],
)
async def generate_signed_url_endpoint(
    knowledge_id: UUID,
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Generate a signed url to download the file from storage.
    """

    knowledge = get_knowledge(knowledge_id)

    validate_brain_authorization(brain_id=knowledge.brain_id, user_id=current_user.id)

    if knowledge.file_name == None:
        raise Exception(f"Knowledge {knowledge_id} has no file_name associated with it")

    file_path_in_storage = f"{knowledge.brain_id}/{knowledge.file_name}"

    file_signed_url = generate_file_signed_url(file_path_in_storage)

    return file_signed_url