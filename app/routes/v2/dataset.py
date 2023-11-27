from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.databases.supabase.dataset import CreateDatasetProperties
from app.models.dataset import DatasetEntity
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.dataset.add_testcase_data_to_dataset import \
    add_testcase_data_to_dataset
from app.repository.dataset.create_dataset import create_dataset
from app.repository.dataset.delete_dataset import delete_dataset
from app.repository.dataset.get_dataset import get_dataset
from app.repository.dataset.get_user_datasets import get_user_datasets
from app.repository.dataset.update_dataset import update_dataset
from app.repository.testcase_data.remove_testcase_data_to_brain_testcase import \
    remove_testcase_data_to_brain_testcase

router = APIRouter()

@router.get(
	"/datasets",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_datasets_route(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[DatasetEntity]:
	"""
	Retrieve all runtimes of the current user
	"""
	return get_user_datasets(current_user.id)

@router.post(
	"/datasets",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_a_dataset_route(
	dataset: CreateDatasetProperties,
	current_user: UserIdentity = Depends(get_current_user)
) -> DatasetEntity:
	"""
	Create a prompt for the current user
	"""
	try:
		response = create_dataset(dataset, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
	
@router.get(
	"/datasets/{dataset_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_dataset_route(
	dataset_id: UUID,
	current_user: UserIdentity = Depends(get_current_user),
) -> DatasetEntity:
	"""
	Retrieve a dataset by id
	"""
	try:
		response = get_dataset(dataset_id, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.put(
	"/datasets/{dataset_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def update_dataset_route(
	dataset_id: UUID,
	dataset: CreateDatasetProperties,
	current_user: UserIdentity = Depends(get_current_user),
) -> DatasetEntity:
	"""
	Update a dataset by id
	"""
	try:
		response = update_dataset(dataset, dataset_id, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.delete(
	"/datasets/{dataset_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def delete_dataset_route(
	dataset_id: UUID,
	current_user: UserIdentity = Depends(get_current_user),
) -> DatasetEntity:
	"""
	Delete a dataset by id
	"""
	try:
		response = delete_dataset(dataset_id, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
	
@router.post(
	"/datasets/add_to_dataset/{dataset_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def add_to_dataset_route(
	dataset_id: UUID,
	testcase_data_id: UUID = Query(..., description="The ID of the testcase data"), 
):
	"""
	Add a testcase data to a dataset
	"""
	try:
		response = add_testcase_data_to_dataset(
			dataset_id, testcase_data_id)
		return {"status": "ok"}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
	
@router.delete(
	"/datasets/remove_from_dataset/{dataset_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def remove_from_dataset_route(
	dataset_id: UUID,
	testcase_data_id: UUID = Query(..., description="The ID of the testcase data"),
):
	"""
	Remove a testcase data from a dataset
	"""
	try:
		response = remove_testcase_data_to_brain_testcase(
			dataset_id, testcase_data_id)
		return {"status": "ok"}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
