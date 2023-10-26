from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.bench.llm_bench import LLMBench
from app.models.brain_testsuite import (BrainTestCaseEntity,
                                        BrainTestSuiteEntity)
from app.models.databases.supabase.brains import (
    CreateBrainTestcaseProperties, CreateBrainTestsuiteProperties,
    UpdateBrainTestcaseProperties, UpdateBrainTestsuiteProperties)
from app.models.testcase_data import (TestCaseDataDescription,
                                      TestCaseDataEntity, TestRun)
from app.models.user_identity import UserIdentity
from app.repository.brain.create_brain_testcase_by_testsuite_id import \
    create_brain_testcase_by_test_suite_id
from app.repository.brain.create_brain_testsuite_by_id import \
    create_brain_testsuite_by_id
from app.repository.brain.delete_brain_testcase_by_testsuite_id import \
    delete_brain_testcase_by_test_suite_id
from app.repository.brain.delete_brain_testsuite_by_id import \
    delete_brain_testsuite_by_id
from app.repository.brain.get_brain_testcase_by_testsuite_id import \
    get_brain_testcase_by_testsuite_id
from app.repository.brain.get_brain_testsuite_by_id import \
    get_brain_testsuite_by_id
from app.repository.brain.update_brain_testcase_by_testsuite_id import \
    update_brain_testcase_by_test_suite_id
from app.repository.brain.update_brain_testsuite_by_id import \
    update_brain_testsuite_by_id
from app.repository.testcase_data.add_testcase_data_to_brain_testcase import \
    add_testcase_data_to_brain_testcase
from app.repository.testcase_data.create_testcase_data_from_message import \
    create_testcase_data_from_message
from app.repository.testcase_data.delete_testcase_data_by_id import \
    delete_testcase_data_by_id
from app.repository.testcase_data.remove_testcase_data_to_brain_testcase import \
    remove_testcase_data_to_brain_testcase

router = APIRouter()

@router.get(
	"/test/brain_testsuite",
	dependencies=[Depends(AuthBearer())],
)
async def get_brain_testsuite_handler(
	brain_id: UUID = Query(..., description="The ID of the brain"),
) -> BrainTestSuiteEntity:
	brain_testsuite = get_brain_testsuite_by_id(brain_id)
	if brain_testsuite is None:
		raise HTTPException(status_code=404, detail="brain testsuite not found")
	return brain_testsuite

@router.post(
		"/test/brain_testsuite", 
		status_code=status.HTTP_201_CREATED, 
		dependencies=[Depends(AuthBearer())])
async def create_brain_testsuite_handler(
	brain_testsuite: CreateBrainTestsuiteProperties,
	brain_id: UUID = Query(..., description="The ID of the brain"),
) -> BrainTestSuiteEntity:
	
	new_brain_testsuite = create_brain_testsuite_by_id(
		brain_id, brain_testsuite)
	if new_brain_testsuite is None:
		raise HTTPException(status_code=404, detail="brain testsuite already exist")
	return new_brain_testsuite

@router.put("/test/brain_testsuite", status_code=status.HTTP_200_OK, dependencies=[Depends(AuthBearer())])
async def update_brain_testsuite_handler(
	brain_testsuite: UpdateBrainTestsuiteProperties,
	brain_id: UUID = Query(..., description="The ID of the brain"),
):
	update_brain_testsuite = update_brain_testsuite_by_id(
		brain_id,
		brain_testsuite,
	)
	if update_brain_testsuite is None:
		raise HTTPException(status_code=404, detail="cannot update brain testsuite maybe brain not found")
	return update_brain_testsuite

@router.delete("/test/brain_testsuite", status_code=status.HTTP_200_OK, dependencies=[Depends(AuthBearer())])
async def delete_brain_testsuite_handler(
	brain_id: UUID = Query(..., description="The ID of the brain"),
):
	delete_brain_testsuite = delete_brain_testsuite_by_id(
		brain_id
	)
	if delete_brain_testsuite is None:
		raise HTTPException(status_code=404, detail="cannot delete brain testsuite maybe brain not found")
	return delete_brain_testsuite


@router.get(
	"/test/brain_testcase",
	dependencies=[Depends(AuthBearer())],
)
async def get_brain_testcase_handler(
	brain_testsuite_id: UUID = Query(..., description="The ID of the brain testsuite"),
) -> List[BrainTestCaseEntity]:
	brain_testcase = get_brain_testcase_by_testsuite_id(brain_testsuite_id)
	return brain_testcase

@router.post(
	"/test/brain_testcase",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def create_brain_testcase_handler(
	brain_testcase: CreateBrainTestcaseProperties,
	brain_testsuite_id: UUID = Query(..., description="The ID of the brain testsuite"),
) -> BrainTestCaseEntity:
	new_brain_testcase = create_brain_testcase_by_test_suite_id(
		brain_testsuite_id, brain_testcase)
	return new_brain_testcase

@router.put("/test/brain_testcase", status_code=status.HTTP_200_OK, dependencies=[Depends(AuthBearer())])
async def update_brain_testcase_handler(
	brain_testcase: UpdateBrainTestcaseProperties,
	brain_testsuite_id: UUID = Query(..., description="The ID of the brain testsuite"),
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase"),

) -> BrainTestCaseEntity:
	update_brain_testcase = update_brain_testcase_by_test_suite_id(
			brain_testsuite_id, brain_testcase_id, brain_testcase)
	if update_brain_testcase is None:
		raise HTTPException(status_code=404, detail="cannot update")
	return update_brain_testcase

@router.delete("/test/brain_testcase", status_code=status.HTTP_200_OK, dependencies=[Depends(AuthBearer())])
async def delete_brain_testcase_handler(
	brain_testsuite_id: UUID = Query(..., description="The ID of the brain testsuite"),
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase"),
) -> BrainTestCaseEntity:
	delete_brain_testcase = delete_brain_testcase_by_test_suite_id(
		brain_testsuite_id,
		brain_testcase_id
	)
	if delete_brain_testcase is None:
		raise HTTPException(status_code=404, detail="cannot delete brain testcase maybe brain_testsuite_id not found")
	return delete_brain_testcase
	
@router.post(
	"/test/message/testcase_data",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def create_testcase_data_from_message_handler(
	description: TestCaseDataDescription,
	message_id: UUID = Query(..., description="The ID of the brain"),
) -> TestCaseDataEntity:
	new_testcase_data = create_testcase_data_from_message(
		message_id, description.description)
	return new_testcase_data

@router.delete(
	"/test/testcase_data", 
	status_code=status.HTTP_200_OK, 
	dependencies=[Depends(AuthBearer())])
async def delete_testcase_handler(
	testcase_data_id: UUID = Query(..., description="The ID of the message"),
) -> TestCaseDataEntity:
	delete_testcase_data = delete_testcase_data_by_id(
		testcase_data_id
	)
	if delete_testcase_data is None:
		raise HTTPException(status_code=404, detail="cannot delete testcase data")
	return delete_testcase_data

@router.post(
	"/test/testcase_data/brain_testcase",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def add_testcase_data_to_brain_testcase_handler(
	testcase_data_id: UUID = Query(..., description="The ID of the testcase data"),
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase"),
):
	new_testcase_data = add_testcase_data_to_brain_testcase(
		brain_testcase_id=brain_testcase_id, 
		testcase_data_id=testcase_data_id
	)
	if len(new_testcase_data.data[0]) > 0:
		return new_testcase_data.data[0]
	else:
		raise HTTPException(status_code=404, detail="cannot add testcase data to brain testcase")
	
@router.delete(
	"/test/testcase_data/brain_testcase",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())],
)
async def remove_testcase_data_to_brain_testcase_handler(
	testcase_data_id: UUID = Query(..., description="The ID of the testcase data"),
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase"),
):
	remove_testcase_data = remove_testcase_data_to_brain_testcase(
		brain_testcase_id=brain_testcase_id,
		testcase_data_id=testcase_data_id
	)
	if len(remove_testcase_data.data[0]) > 0:
		return remove_testcase_data.data[0]
	else:
		raise HTTPException(status_code=404, detail="cannot remove testcase data to brain testcase")


@router.post(
	"/test/brain/{chat_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_testcase_for_a_brain(
	test_run: TestRun,
	chat_id: UUID,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	current_user: UserIdentity = Depends(get_current_user),
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase")
):
	bench = LLMBench(
		brain_id=str(brain_id),
		chat_id=str(chat_id),
		brain_testcase_id=str(brain_testcase_id),
		current_user=current_user
	)
	response = bench.run(
		run_name=test_run.run_name,
		batch_size=test_run.batch_size,
	)
	return response

