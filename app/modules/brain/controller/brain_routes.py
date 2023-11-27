

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.logger import get_logger
from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.middlewares.auth.brain_authorization import has_brain_authorization
from app.modules.brain.entity.brain import (BrainEntity, CreateBrainProperties,
                                            CreateFullBrainProperties,
                                            CreateRuntimeProperties,
                                            FullBrainEntityWithRights,
                                            RoleEnum, RuntimeType,
                                            UpdateBrainProperties)
from app.modules.brain.service.brain_service import BrainService
from app.modules.user.entity.user_identity import UserIdentity
from app.modules.user_usage.service.user_usage_service import UserUsageService

brain_router = APIRouter()

brain_Service = BrainService()
user_usage_service = UserUsageService()

logger = get_logger(__name__)


# set as default brain
@brain_router.post(
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

	brain_Service.set_as_default_brain_for_user(user.id, brain_id)

	return {"message": f"Brain {brain_id} has been set as default brain."}

@brain_router.get(
	"/brains/",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def brain_endpoint(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[FullBrainEntityWithRights]:
	"""
	Retrieve all brains for the current user.

	- `current_user`: The current authenticated user.
	- Returns a list of all brains registered for the user.

	This endpoint retrieves all the brains associated with the current authenticated user. It returns a list of brains objects
	containing the brain ID, brain name for each brain, the right for the brain (Owner, Editor, Viewer) and the brain status
	"""
	brains = brain_Service.get_user_brains(current_user.id)
	return brains

# get default brain
@brain_router.get(
	"/brains/default/", status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_default_brain_endpoint(
	current_user: UserIdentity = Depends(get_current_user),
) -> FullBrainEntityWithRights:
	"""
	Retrieve the default brain for the current user. If the user doesnt have one, it creates one.

	- `current_user`: The current authenticated user.
	- Returns the default brain for the user.

	This endpoint retrieves the default brain associated with the current authenticated user.
	The default brain is defined as the brain marked as default in the brains_users table.
	"""

	brain = brain_Service.get_default_user_brain_or_create_new(current_user.id)
	return brain

# get details of a specific brain
@brain_router.get(
	"/brains/{brain_id}/",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer()), Depends(has_brain_authorization())]
)
async def get_brain_endpoint(
	brain_id: UUID,
) -> FullBrainEntityWithRights | None:
	"""
	Retrieve details of a specific brain by brain ID.

	- `brain_id`: The ID of the brain to retrieve details for.
	- Returns the brain details.
	- Raises a 404 error if the brain ID is not found.

	This endpoint retrieves the details of a specific brain identified by the provided brain ID. It returns the brain ID and its
	history, which includes the brain messages exchanged in the brain.
	"""

	brain_details = brain_Service.get_brain_details(brain_id)
	if brain_details is None:
		raise HTTPException(
			status_code=404,
			detail="Brain details not found",
		)

	return brain_details


# create new brain
@brain_router.post(
	"/brains/",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_brain_endpoint(
	brain: CreateBrainProperties,
	current_user: UserIdentity = Depends(get_current_user),
) -> FullBrainEntityWithRights:
	"""
	Create a new brain with given
		name
		status
		model
		max_tokens
		temperature
		runtime
		teacher_runtime
	In the brains table & in the brains_users table and put the creator user as 'Owner'
	"""

	user_brains = brain_Service.get_user_brains(current_user.id)
	
	userSettings = user_usage_service.get_user_settings(current_user.id)
	
	if len(user_brains) >= userSettings.get("max_brains", 5):
		raise HTTPException(
			status_code=429,
			detail=f"Maximum number of brains reached ({userSettings.get('max_brains', 5)}).",
		)
	# create runtime and teacher runtime for the brain
	runtime = brain_Service.create_runtime(
		runtime=CreateRuntimeProperties(
			type=RuntimeType.OpenAi,
			name="Default Runtime",
			model="gpt-3.5-turbo",
			max_tokens=256,
			temperature=0.9,
			openai_api_key=current_user.openai_api_key
			if current_user.openai_api_key else "place your openai api key here",
		),
		user_id=current_user.id,
	)
	teacher_runtime = brain_Service.create_runtime(
		runtime=CreateRuntimeProperties(
			type=RuntimeType.OpenAi,
			name="Default Runtime",
			model="gpt-3.5-turbo",
			max_tokens=256,
			temperature=0.9,
			openai_api_key=current_user.openai_api_key
			if current_user.openai_api_key else "place your openai api key here",
		),
		user_id=current_user.id,
	)
	brain_with_runtime = CreateFullBrainProperties(
		name=brain.name,
		description=brain.description,
		status=brain.status,
		prompt_id=brain.prompt_id,
		runtime_id=str(runtime.id),
		teacher_runtime_id=str(teacher_runtime.id),
	)
	# create brain entity
	new_brain = brain_Service.create_brain(
		brain_with_runtime,
	)
		
	default_brain = brain_Service.get_user_default_brain(current_user.id)
	if default_brain:
		logger.info(f"Default brain already exists for user {current_user.id}")
		brain_Service.create_brain_user(
			user_id=current_user.id,
			brain_id=new_brain.id,
			rights=RoleEnum.Owner,
			is_default_brain=False,
		)
	else:
		logger.info(
			f"Default brain does not exist for user {current_user.id}. It will be created."
		)
		brain_Service.create_brain_user(
			user_id=current_user.id,
			brain_id=new_brain.id,
			rights=RoleEnum.Owner,
			is_default_brain=True,
		)
	
	return FullBrainEntityWithRights(
		id=new_brain.id,
		name=new_brain.name,
		description=new_brain.description,
		status=new_brain.status,
		prompt_id=new_brain.prompt_id,
		runtime=runtime,
		teacher_runtime=teacher_runtime,
		last_update=new_brain.last_update,
		rights=RoleEnum.Owner,
	)

# update existing brain
@brain_router.put(
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
	brain_to_update: UpdateBrainProperties,
) -> BrainEntity | None:
	"""
	Update an existing brain with new brain configuration 
	Raise a 404 error if the brain ID is not found.
	"""

	# Remove prompt if it is private and no longer used by brain
	existing_brain = brain_Service.get_brain_details(brain_id)
	if existing_brain is None:
		raise HTTPException(
			status_code=404,
			detail="Brain not found",
		)

	update_brain = brain_Service.update_brain_by_id(brain_id, brain_to_update)

	return update_brain

# delete existing brain
@brain_router.delete(
	"/brains/{brain_id}/",
	status_code=status.HTTP_200_OK,
	dependencies=[
		Depends(AuthBearer()),
		Depends(has_brain_authorization([RoleEnum.Owner]))
	],
)
async def delete_brain_endpoint(
	brain_id: UUID,
) -> BrainEntity | None:
	"""
	Delete an existing brain by brain ID
	Raise a 404 error if the brain ID is not found.
	"""

	existing_brain = brain_Service.get_brain_details(brain_id)
	if existing_brain is None:
		raise HTTPException(
			status_code=404,
			detail="Brain not found",
		)

	brain_Service.delete_brain_by_id(brain_id)

	return existing_brain