from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models import UserIdentity, UserUsage
from app.models.brain_entity import (BrainEntity, MinimalBrainEntity,
                                     PublicBrain)
from app.models.databases.supabase.brains import (BrainInputRequest,
                                                  BrainUpdatableProperties,
                                                  CreateBrainProperties,
                                                  CreatedBrainOutput)
from app.repository.brain import (create_brain, create_brain_user,
                                  get_brain_details,
                                  get_default_user_brain_or_create_new,
                                  get_public_brains, get_user_brains,
                                  get_user_default_brain,
                                  set_as_default_brain_for_user)
from app.repository.brain.create_brain_meta_brain import \
    create_brain_meta_brain
from app.repository.brain.delete_brain_user import delete_brain_user
from app.repository.brain.get_question_context_from_brain import \
    get_question_context_from_brain
from app.repository.brain.update_brain import update_brain_by_id
from app.routes.authorizations.brain_authorization import \
    has_brain_authorization
from app.routes.authorizations.meta_brain_authorization import \
    has_meta_brain_authorization
from app.routes.authorizations.types import RoleEnum

logger = get_logger(__name__)

router = APIRouter()

# get all brains
@router.get("/brains/", status_code=status.HTTP_200_OK,
												dependencies=[Depends(AuthBearer())])
async def brain_endpoint(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[MinimalBrainEntity]:
	"""
	Retrieve all brains for the current user.

	- `current_user`: The current authenticated user.
	- Returns a list of all brains registered for the user.

	This endpoint retrieves all the brains associated with the current authenticated user. It returns a list of brains objects
	containing the brain ID, brain name for each brain, the right for the brain (Owner, Editor, Viewer) and the brain status
	"""
	brains = get_user_brains(current_user.id)
	return brains

# get all the public brains
@router.get(
	"/brains/public", status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def public_brains_endpoint() -> list[PublicBrain]:
	"""
	Retrieve all Ally AI public brains
	"""
	return get_public_brains()


# get default brain
@router.get(
	"/brains/default/", status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_default_brain_endpoint(
	current_user: UserIdentity = Depends(get_current_user),
) -> BrainEntity:
	"""
	Retrieve the default brain for the current user. If the user doesnt have one, it creates one.

	- `current_user`: The current authenticated user.
	- Returns the default brain for the user.

	This endpoint retrieves the default brain associated with the current authenticated user.
	The default brain is defined as the brain marked as default in the brains_users table.
	"""

	brain = get_default_user_brain_or_create_new(current_user)
	return brain

# get details of a specific brain
@router.get(
	"/brains/{brain_id}/",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer()), Depends(has_brain_authorization())]
)
async def get_brain_endpoint(
	brain_id: UUID,
) -> BrainEntity | None:
	"""
	Retrieve details of a specific brain by brain ID.

	- `brain_id`: The ID of the brain to retrieve details for.
	- Returns the brain details.
	- Raises a 404 error if the brain ID is not found.

	This endpoint retrieves the details of a specific brain identified by the provided brain ID. It returns the brain ID and its
	history, which includes the brain messages exchanged in the brain.
	"""

	brain_details = get_brain_details(brain_id)
	if brain_details is None:
		raise HTTPException(
			status_code=404,
			detail="Brain details not found",
		)

	return brain_details


# create new brain
@router.post("/brains/", status_code=status.HTTP_201_CREATED,
													dependencies=[Depends(AuthBearer())])
async def create_brain_endpoint(
	brain: CreateBrainProperties,
	current_user: UserIdentity = Depends(get_current_user),
) -> CreatedBrainOutput:
	"""
	Create a new brain with given
		name
		status
		model
		max_tokens
		temperature
	In the brains table & in the brains_users table and put the creator user as 'Owner'
	"""

	user_brains = get_user_brains(current_user.id)
	
	userDailyUsage = UserUsage(
		id=current_user.id,
		email=current_user.email,
		openai_api_key=current_user.openai_api_key,
	)
	userSettings = userDailyUsage.get_user_settings()

	if len(user_brains) >= userSettings.get("max_brains", 5):
		raise HTTPException(
			status_code=429,
			detail=f"Maximum number of brains reached ({userSettings.get('max_brains', 5)}).",
		)

	new_brain = create_brain(
		brain,
	)
	default_brain = get_user_default_brain(current_user.id)
	if default_brain:
		logger.info(f"Default brain already exists for user {current_user.id}")
		create_brain_user(
			user_id=current_user.id,
			brain_id=new_brain.brain_id,
			rights=RoleEnum.Owner,
			is_default_brain=False,
		)
	else:
		logger.info(
			f"Default brain does not exist for user {current_user.id}. It will be created."
		)
		create_brain_user(
			user_id=current_user.id,
			brain_id=new_brain.brain_id,
			rights=RoleEnum.Owner,
			is_default_brain=True,
		)

	return {
		"brain_id": new_brain.brain_id,
		"name": brain.name,
		"rights": "Owner",
	}

# update existing brain
@router.put(
	"/brains/{brain_id}/",
	status_code=status.HTTP_200_OK,
	dependencies=[
		Depends(
			AuthBearer(),
		),
		Depends(has_brain_authorization([RoleEnum.Editor, RoleEnum.Owner])),
	],
)
async def update_brain_endpoint(
	brain_id: UUID,
	brain_to_update: BrainUpdatableProperties,
) -> BrainEntity | None:
	"""
	Update an existing brain with new brain configuration 
	Raise a 404 error if the brain ID is not found.
	"""

	# Remove prompt if it is private and no longer used by brain
	existing_brain = get_brain_details(brain_id)
	if existing_brain is None:
		raise HTTPException(
			status_code=404,
			detail="Brain not found",
		)

	# if brain_to_update.prompt_id is None:
	# 	prompt_id = existing_brain.prompt_id
	# 	if prompt_id is not None:
	# 		prompt = get_prompt_by_id(prompt_id)
	# 		if prompt is not None and prompt.status == "private":
	# 			delete_prompt_by_id(prompt_id)

	if brain_to_update.status == "private" and existing_brain.status == "public":
		delete_brain_user(brain_id)

	update_brain = update_brain_by_id(brain_id, brain_to_update)

	return update_brain

# set as default brain
@router.post(
	"/brains/{brain_id}/default",
	status_code=status.HTTP_200_OK,
	dependencies=[
		Depends(
			AuthBearer(),
		),
		Depends(has_brain_authorization()),
	],
)
async def set_as_default_brain_endpoint(
	brain_id: UUID,
	user: UserIdentity = Depends(get_current_user),
):
	"""
	Set a brain as default for the current user.
	"""

	set_as_default_brain_for_user(user.id, brain_id)

	return {"message": f"Brain {brain_id} has been set as default brain."}

# create a relation between brain and meta brain
@router.post(
	"/brains/{brain_id}/{meta_brain_id}",
	dependencies=[
		Depends(
			AuthBearer(),
		),
		Depends(has_brain_authorization()),
		Depends(has_meta_brain_authorization()),
	],
)
async def set_brain_meta_brain_relation(
	brain_id: UUID,
	meta_brain_id: UUID,
):
	"""
	Set a brain and meta brain relation.
	"""
	create_brain_meta_brain(brain_id, meta_brain_id)
	return {"message": f"set the relation for meta brain {meta_brain_id} and brain {brain_id}"}

@router.post(
	"/question_context/{brain_id}",
	dependencies=[
		Depends(
			AuthBearer(),
		),
		Depends(has_brain_authorization()),
	],
	tags=["Brain"],
)
async def get_question_context_from_brain_endpoint(
	brain_id: UUID,
	request: BrainInputRequest,
):
	"""
	Get question context from brain
	"""

	context = get_question_context_from_brain(brain_id, request.chat_input)

	return {"context": context}