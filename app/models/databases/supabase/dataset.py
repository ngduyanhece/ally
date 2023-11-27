from uuid import UUID

from pydantic import BaseModel

from app.models.databases.repository import Repository
from app.models.dataset import DatasetEntity


class CreateDatasetProperties(BaseModel):
	name: str
	description: str


class Dataset(Repository):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def get_user_datasets(self, user_id: UUID) -> list[DatasetEntity]:
		"""
		Returns all dataset of a user
		"""
		response = (
			self.db.from_("datasets")
			.select("*")
			.filter("user_id", "eq", str(user_id))
			.execute()
		).data
		datasets: list[DatasetEntity] = []
		for dataset in response:
			datasets.append(DatasetEntity(
				id=dataset["id"],
				name=dataset["name"],
				description=dataset["description"],
			))
		return datasets
	
	def create_dataset(
			self, dataset: CreateDatasetProperties, user_id: UUID) -> DatasetEntity:
		"""
		Creates a dataset
		"""
		response = (
			self.db.from_("datasets")
			.insert(
				{
					"name": dataset.name,
					"description": dataset.description,
					"user_id": str(user_id),
				}
			)
			.execute()
		).data[0]
		return DatasetEntity(
			id=response["id"],
			name=response["name"],
			description=response["description"],
		)
	
	def get_dataset(self, dataset_id: UUID, user_id: UUID) -> DatasetEntity:
		"""
		Get a dataset by its id
		"""
		response = (
			self.db.from_("datasets")
			.select("*")
			.filter("id", "eq", str(dataset_id))
			.filter("user_id", "eq", str(user_id))
			.execute()
		).data[0]
		if not response:
			return None
		return DatasetEntity(
			id=response["id"],
			name=response["name"],
			description=response["description"],
		)
	
	def update_dataset(
			self, 
			dataset: CreateDatasetProperties,
			dataset_id: UUID, user_id: UUID) -> DatasetEntity | None:
		"""
		Update a dataset
		"""
		response = (
			self.db.from_("datasets")
			.update(
				{
					"name": dataset.name,
					"description": dataset.description,
				}
			)
			.filter("id", "eq", str(dataset_id))
			.filter("user_id", "eq", str(user_id))
			.execute()
		).data
		
		if not response:
			raise Exception("Dataset not found")
		else:
			data = response[0]
			return DatasetEntity(
				id=data["id"],
				name=data["name"],
				description=data["description"],
			)

	def delete_dataset(self, dataset_id: UUID, user_id: UUID) -> DatasetEntity:
		"""
		Delete a dataset
		"""
		response = (
			self.db.from_("datasets")
			.delete()
			.filter("id", "eq", str(dataset_id))
			.filter("user_id", "eq", str(user_id))
			.execute()
		).data
		if not response:
				raise Exception("Dataset not found")
		else:
			data = response[0]
			return DatasetEntity(
				id=data["id"],
				name=data["name"],
				description=data["description"],
			)
		
	def create_dataset_testcase_data(
			self, dataset_id: UUID, testcase_data_id: UUID):
		"""
		Adds a testcase data to a dataset
		"""
		response = (
			self.db.from_("datasets_testcase_data")
			.insert(
				{
					"dataset_id": str(dataset_id),
					"testcase_data_id": str(testcase_data_id),
				}
			)
			.execute()
		).data
		if not response:
				raise Exception("cannot add testcase data to dataset")
		else:
			data = response[0]
			return data
		
	def delete_dataset_testcase_data(
			self, dataset_id: UUID, testcase_data_id: UUID):
		"""
		Removes a testcase data from a dataset
		"""
		response = (
			self.db.from_("datasets_testcase_data")
			.delete()
			.filter("dataset_id", "eq", str(dataset_id))
			.filter("testcase_data_id", "eq", str(testcase_data_id))
			.execute()
		).data
		if not response:
				raise Exception("cannot remove testcase data from dataset")
		else:
			data = response[0]
			return data
		
