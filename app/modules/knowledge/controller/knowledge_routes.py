import os
from typing import Optional
from uuid import UUID

from fastapi import (APIRouter, Depends, HTTPException, Query, Request,
                     UploadFile)

from app.logger import get_logger
from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.middlewares.auth.brain_authorization import \
    validate_brain_authorization
from app.modules.brain.entity.brain import RoleEnum
from app.modules.knowledge.entity.knowledge import CreateKnowledgeProperties
from app.modules.knowledge.service.knowledge_service import KnowledgeService
from app.modules.notification.entity.notification import (
    CreateNotificationProperties, NotificationsStatusEnum,
    UpdateNotificationProperties)
from app.modules.notification.service.notification_service import \
    NotificationService
from app.modules.user.entity.user_identity import UserIdentity

logger = get_logger(__name__)

knowledge_router = APIRouter()
notification_service = NotificationService()
knowledge_service = KnowledgeService()

@knowledge_router.get("/knowledge/healthz", tags=["Health"])
async def healthz():
	return {"status": "ok"}

@knowledge_router.post(
	"/upload", 
	dependencies=[Depends(AuthBearer())])
async def upload_file(
    request: Request,
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
		file_in_storage = knowledge_service.upload_file_storage(file_content, filename_with_brain_id)
		logger.info(f"File {file_in_storage} uploaded successfully")

	except Exception as e:
		logger.error(f"Error uploading file to storage: {e}")
		notification_message = {
				"status": "error",
				"message": "There was an error uploading the file. Please check the file and try again. If the issue persist, please open an issue on Github",
				"name": uploadFile.filename if uploadFile else "Last Upload File",
		}
		notification_service.update_notification_by_id(
			upload_notification.id, UpdateNotificationProperties(
				status=NotificationsStatusEnum.Done,
				message=str(notification_message),
			),
		)
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
	)
	added_knowledge = knowledge_service.add_knowledge(knowledge_to_add)
	logger.info(f"Knowledge {added_knowledge} added successfully")
	