import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from modal import Function

from app.logger import get_logger
from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.middlewares.auth.brain_authorization import (
    has_brain_authorization, validate_brain_authorization)
from app.modules.brain.entity.brain import RoleEnum
from app.modules.brain.service.brain_service import BrainService
from app.modules.file.service.file_service import FileService
from app.modules.knowledge.entity.knowledge import (CreateKnowledgeProperties,
                                                    KnowledgeEntity,
                                                    KnowledgeStatus)
from app.modules.knowledge.service.knowledge_service import KnowledgeService
from app.modules.notification.entity.notification import (
    CreateNotificationProperties, NotificationsStatusEnum)
from app.modules.notification.service.notification_service import \
    NotificationService
from app.modules.user.entity.user_identity import UserIdentity

logger = get_logger(__name__)

knowledge_router = APIRouter()
notification_service = NotificationService()
knowledge_service = KnowledgeService()
brain_service = BrainService()
file_service = FileService()

@knowledge_router.get("/knowledge/healthz", tags=["Health"])
async def healthz():
	return {"status": "ok"}

@knowledge_router.post(
	"/upload",
	dependencies=[Depends(AuthBearer())])
async def upload_file(
	uploadFile: UploadFile,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	chat_id: Optional[UUID] = Query(None, description="The ID of the chat"),
	current_user: UserIdentity = Depends(get_current_user),
):
	validate_brain_authorization(
		brain_id, current_user.id, [RoleEnum.Editor, RoleEnum.Owner]
	)
	upload_notification = None

	if chat_id:
		upload_notification = notification_service.add_notification(
			CreateNotificationProperties(
				action="UPLOAD",
				chat_id=chat_id,
				status=NotificationsStatusEnum.Pending,
			)
		)
	file_content = await uploadFile.read()
	filename_with_brain_id = str(brain_id) + "/" + str(uploadFile.filename)
	try:
		file_in_storage = file_service.upload_file_storage(
			file_content, filename_with_brain_id)
		logger.info(f"File {file_in_storage} uploaded successfully")

	except Exception as e:
		logger.error(f"Error uploading file to storage: {e}")
		notification_message = {
				"status": "error",
				"message": "There was an error uploading the file. Please check the file and try again. If the issue persist, please open an issue on Github",
				"name": uploadFile.filename if uploadFile else "Last Upload File",
		}
		# notification_service.update_notification_by_id(
		# 	upload_notification.id, UpdateNotificationProperties(
		# 		status=NotificationsStatusEnum.Done,
		# 		message=str(notification_message),
		# 	),
		# )
		if "The resource already exists" in str(e):
			raise HTTPException(
				status_code=403,
				detail=f"File {uploadFile.filename} already exists in storage.",
			)
		else:
			raise HTTPException(
				status_code=500, detail=f"Failed to upload file to storage. {e}"
			)

	knowledge_to_add = CreateKnowledgeProperties(
		brain_id=brain_id,
		file_name=uploadFile.filename,
		extension=os.path.splitext(
			uploadFile.filename  # pyright: ignore reportPrivateUsage=none
		)[-1].lower(),
		status=KnowledgeStatus.Pending,
		message="",
	)
	added_knowledge = knowledge_service.add_knowledge(knowledge_to_add)
	logger.info(f"Knowledge {added_knowledge} added successfully")
	process_file_and_notify = Function.lookup(
		"file-process-and-notify", "file_process_and_notify")
	_ = process_file_and_notify.spawn(
		filename_with_brain_id,
		uploadFile.filename,
		brain_id,
		knowledge_id=added_knowledge.id
	)
	# await file_service.process_file_and_notify(
	# 	file_name=filename_with_brain_id,
	# 	file_original_name=uploadFile.filename,
	# 	brain_id=brain_id,
	# 	knowledge_id=added_knowledge.id if added_knowledge.id else None,
	# )
	return {"message": "File processing has started."}


@knowledge_router.get(
	"/knowledge", dependencies=[Depends(AuthBearer())]
)
async def list_knowledge_in_brain_endpoint(
		brain_id: UUID = Query(..., description="The ID of the brain"),
		current_user: UserIdentity = Depends(get_current_user),
) -> list[KnowledgeEntity]:
	"""
	Retrieve and list all the knowledge in a brain.
	"""

	validate_brain_authorization(brain_id=brain_id, user_id=current_user.id)

	knowledges = knowledge_service.get_all_knowledge_in_brain(brain_id)
	return knowledges

@knowledge_router.delete(
	"/knowledge/{knowledge_id}",
	dependencies=[
		Depends(AuthBearer()),
		Depends(has_brain_authorization(RoleEnum.Owner)),
	],
)
async def delete_endpoint(
	knowledge_id: UUID,
	current_user: UserIdentity = Depends(get_current_user),
	brain_id: UUID = Query(..., description="The ID of the brain"),
):
	"""
	Delete a specific knowledge from a brain.
	"""
	try:
		knowledge = knowledge_service.get_knowledge(knowledge_id)
		file_name = knowledge.file_name if knowledge.file_name else knowledge.url
		knowledge_service.remove_knowledge(knowledge_id)

		if knowledge.file_name:
			file_service.delete_file_from_storage(
				f"{brain_id}/{knowledge.file_name}")
			brain_service.delete_file_from_brain(brain_id, knowledge.file_name)
		elif knowledge.url:
			brain_service.delete_file_from_brain(brain_id, knowledge.url)

		return {
			"message": f"""{file_name} of brain {brain_id}
			has been deleted by user {current_user.email}."""
		}
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Failed to delete knowledge. {e}"
		)