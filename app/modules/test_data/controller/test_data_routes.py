
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.modules.test_data.entity.test_data import (MessageLabel,
                                                    MessageLabelOutput,
                                                    TestCaseDataDescription,
                                                    TestCaseDataEntity)
from app.modules.test_data.service.test_data_service import TestDataService
from app.modules.user.entity.user_identity import UserIdentity

test_data_router = APIRouter()
test_data_service = TestDataService()

@test_data_router.post(
	"/test_data/message/testcase_data",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def create_testcase_data_from_message_handler(
	description: TestCaseDataDescription,
	message_id: UUID = Query(..., description="The ID of the message"),
) -> TestCaseDataEntity:
	new_testcase_data = test_data_service.create_testcase_data_from_message(
		message_id, description.description)
	return new_testcase_data

@test_data_router.get(
	"/test_data/message/label",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_label_for_message_handler(
	message_id: UUID = Query(..., description="The ID of the message"),
) -> MessageLabelOutput:
	response = test_data_service.get_message_label_by_id(message_id)
	if response is None:
		raise HTTPException(status_code=404, detail="Label not found")
	return response

@test_data_router.post(
	"/test_data/message/label",
	status_code=status.HTTP_201_CREATED, 
	dependencies=[Depends(AuthBearer())])
async def create_label_for_message_handler(
	message_label: MessageLabel,
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
) -> MessageLabel | None:
	response = test_data_service.create_message_label_by_id(
		message_label, message_id, current_user.id)
	if response is None:
		raise HTTPException(status_code=400, detail="Message label already exists")
	else:
		return response
	

@test_data_router.put(
	"/test_data/message/label",
	status_code=status.HTTP_200_OK, 
	dependencies=[Depends(AuthBearer())])
async def update_label_for_message_handler( 
	message_label: MessageLabel,
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	try:
		response = test_data_service.update_message_label_by_id(
			message_label, message_id, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail="cannot update label")
	
@test_data_router.delete(
	"/test_data/message/label",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def delete_label_for_message_handler(
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	try:
		response = test_data_service.delete_message_label_by_id(
			message_id, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail="label not found")