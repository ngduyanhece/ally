
from uuid import UUID

from fastapi import APIRouter, Query, status
from fastapi.params import Depends

from ally.environments.base import StaticEnvironment
from ally.utils.internal_data import InternalDataFrame
from ally.utils.logs import print_dataframe
from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.user_identity import UserIdentity
from app.repository.testcase_data.get_all_testcase_data_from_brain_testcase import \
    get_all_testcase_data_from_brain_testcase

router = APIRouter()
logger = get_logger(__name__)

@router.post(
	"/learn",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_brain_learning_process(
	brain_testcase_id: UUID = Query(..., description="The ID of the brain testcase"),
	current_user: UserIdentity = Depends(get_current_user),
):
	testcase_data = get_all_testcase_data_from_brain_testcase(brain_testcase_id)
	env = StaticEnvironment(
		df=InternalDataFrame(testcase_data),
		ground_truth_columns={"reference_output": "reference_output"}
	)
	print_dataframe(InternalDataFrame([dict(data) for data in testcase_data]))
	logger.info(env)