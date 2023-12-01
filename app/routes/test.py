from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.bench.llm_bench import LLMBench
from app.bench.user_simulator_bench import UserSimulatorBench
from app.llm.llm_brain import LLMBrain
from app.llm.llm_user_simulator import LLMUserSimulator
from app.logger import get_logger
from app.models.brain_testsuite import (BrainTestCaseEntity,
                                        BrainTestSuiteEntity)
from app.models.chats import ChatInput
from app.models.databases.supabase.brains import (
    CreateBrainTestcaseProperties, CreateBrainTestsuiteProperties,
    UpdateBrainTestcaseProperties, UpdateBrainTestsuiteProperties)
from app.models.testcase_data import (TestCaseDataEntity, TestRun)
from app.modules.user.entity.user_identity import UserIdentity
from app.modules.user.repository.get_user_identity import get_user_identity
from app.repository.brain.create_brain_testcase_by_testsuite_id import \
    create_brain_testcase_by_test_suite_id
from app.repository.brain.create_brain_testsuite_by_id import \
    create_brain_testsuite_by_id
from app.repository.brain.delete_brain_testcase_by_testsuite_id import \
    delete_brain_testcase_by_test_suite_id
from app.repository.brain.delete_brain_testsuite_by_id import \
    delete_brain_testsuite_by_id
from app.repository.brain.get_brain_details import get_brain_details
from app.repository.brain.get_brain_testcase_by_testsuite_id import \
    get_brain_testcase_by_testsuite_id
from app.repository.brain.get_brain_testsuite_by_id import \
    get_brain_testsuite_by_id
from app.repository.brain.update_brain_testcase_by_testsuite_id import \
    update_brain_testcase_by_test_suite_id
from app.repository.brain.update_brain_testsuite_by_id import \
    update_brain_testsuite_by_id
from app.repository.task_goal.get_goal_by_brain_id_and_goal_id import \
    get_task_goal_by_brain_id_goal_id
from app.repository.testcase_data.add_testcase_data_to_brain_testcase import \
    add_testcase_data_to_brain_testcase
from app.repository.testcase_data.delete_testcase_data_by_id import \
    delete_testcase_data_by_id
from app.repository.testcase_data.remove_testcase_data_to_brain_testcase import \
    remove_testcase_data_to_brain_testcase

logger = get_logger(__name__)

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
		raise HTTPException(status_code=404, detail="cannot delete brain testsuite maybe brain testsuite not found")
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
	

@router.delete(
	"/test/testcase_data", 
	status_code=status.HTTP_200_OK, 
	dependencies=[Depends(AuthBearer())])
async def delete_testcase_handler(
	testcase_data_id: UUID = Query(..., description="The ID of the testcase data"),
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
	try:
		new_testcase_data = add_testcase_data_to_brain_testcase(
			brain_testcase_id=brain_testcase_id, 
			testcase_data_id=testcase_data_id
		)
		return new_testcase_data.data
	except Exception as e:
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
	if len(remove_testcase_data.data) > 0:
		return remove_testcase_data.data
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
	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)

		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
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
	return response.data[0]

@router.post(
	"/test/user_simulator",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_test_for_a_brain_with_user_simulator(
	brain_id: UUID = Query(..., description="The ID of the brain"),
	user_simulator_id: UUID = Query(..., description="The ID of the user simulator"),
	current_user: UserIdentity = Depends(get_current_user),
):
	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)
		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
	brain = get_brain_details(brain_id)
	llm_brain = LLMBrain(
		chat_id="",
		model=brain.model,
		max_tokens=brain.max_tokens,
		temperature=brain.temperature,
		brain_id=str(brain_id),
		user_openai_api_key=str(current_user.openai_api_key) if current_user.openai_api_key else str(brain.openai_api_key),
		prompt_id=str(brain.prompt_id)
	)

	llm_user_simulator = LLMUserSimulator(
		brain_id=str(user_simulator_id),
		user_openai_api_key=str(current_user.openai_api_key)
	)

	# user simulator share the same knowledge of brain
	llm_user_simulator.vector_store = llm_brain.vector_store

	logger.info(f"current_user {current_user}")

	user_simulator_bench = UserSimulatorBench(
		llm_brain=llm_brain,
		llm_user_simulator=llm_user_simulator,
		user_id=current_user.id,
		max_turns=5
	)
	user_simulator_bench.simulate()


@router.post(
	"/test/add_question_to_user_simulator/{user_simulator_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def add_question_to_user_simulator(
	user_simulator_id: UUID,
	chat_input: ChatInput,
	chat_id: UUID = Query(..., description="The ID of the chat"),
	goal_id: UUID = Query(..., description="The ID of the user simulator goal"),
	brain_id: UUID = Query(..., description="The ID of the brain"),
	current_user: UserIdentity = Depends(get_current_user),
):
	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)
		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
	
	brain = get_brain_details(user_simulator_id)
	goal = get_task_goal_by_brain_id_goal_id(brain_id, goal_id)

	llm_user_simulator = LLMUserSimulator(
		brain=brain,
		user_openai_api_key=str(current_user.openai_api_key),
		goal=goal
	)
	chat_answer = llm_user_simulator.generate_answer(chat_id, chat_input)
	return chat_answer




	




	
