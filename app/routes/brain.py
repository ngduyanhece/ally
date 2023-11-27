
from fastapi import APIRouter, Depends, status

from app.auth.auth_bearer import AuthBearer
from app.logger import get_logger
from app.models.brain_entity import PublicBrain
from app.repository.brain import get_public_brains

logger = get_logger(__name__)

router = APIRouter()

# get all brains

# get all the public brains
@router.get(
	"/brains/public", status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def public_brains_endpoint() -> list[PublicBrain]:
	"""
	Retrieve all Ally AI public brains
	"""
	return get_public_brains()

# # set as default brain
# @router.post(
# 	"/brains/{brain_id}/default",
# 	status_code=status.HTTP_200_OK,
# 	dependencies=[
# 		Depends(
# 			AuthBearer(),
# 		),
# 		Depends(has_brain_authorization()),
# 	],
# )
# async def set_as_default_brain_endpoint(
# 	brain_id: UUID,
# 	user: UserIdentity = Depends(get_current_user),
# ):
# 	"""
# 	Set a brain as default for the current user.
# 	"""

# 	set_as_default_brain_for_user(user.id, brain_id)

# 	return {"message": f"Brain {brain_id} has been set as default brain."}

# # create a relation between brain and meta brain
# @router.post(
# 	"/brains/{brain_id}/{meta_brain_id}",
# 	dependencies=[
# 		Depends(
# 			AuthBearer(),
# 		),
# 		Depends(has_brain_authorization()),
# 		Depends(has_meta_brain_authorization()),
# 	],
# )
# async def set_brain_meta_brain_relation(
# 	brain_id: UUID,
# 	meta_brain_id: UUID,
# ):
# 	"""
# 	Set a brain and meta brain relation.
# 	"""
# 	create_brain_meta_brain(brain_id, meta_brain_id)
# 	return {"message": f"set the relation for meta brain {meta_brain_id} and brain {brain_id}"}

# @router.post(
# 	"/question_context/{brain_id}",
# 	dependencies=[
# 		Depends(
# 			AuthBearer(),
# 		),
# 		Depends(has_brain_authorization()),
# 	],
# 	tags=["Brain"],
# )
# async def get_question_context_from_brain_endpoint(
# 	brain_id: UUID,
# 	request: BrainInputRequest,
# ):
# 	"""
# 	Get question context from brain
# 	"""

# 	context = get_question_context_from_brain(brain_id, request.chat_input)

# 	return {"context": context}