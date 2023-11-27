import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.logger import get_logger
from app.models.brain_entity import (BrainEntity, FullBrainEntity,
                                     InfosBrainEntity, MinimalBrainEntity,
                                     PublicBrain)
from app.models.brain_testsuite import BrainTestSuiteEntity
from app.models.databases.repository import Repository
from app.repository.runtime.get_runtime_by_id import get_runtime_by_id

logger = get_logger(__name__)


class CreateBrainProperties(BaseModel):
	name: Optional[str] = "Default brain"
	description: Optional[str] = "This is a description"
	status: Optional[str] = "private"
	prompt_id: Optional[UUID] = None

	def dict(self, *args, **kwargs):
		brain_dict = super().model_dump(*args, **kwargs)
		if brain_dict.get("prompt_id"):
			brain_dict["prompt_id"] = str(brain_dict.get("prompt_id"))
		return brain_dict
	
class CreateFullBrainProperties(BaseModel):
	name: Optional[str] = "Default brain"
	description: Optional[str] = "This is a description"
	status: Optional[str] = "private"
	prompt_id: Optional[UUID] = None
	runtime_id: Optional[str] = None
	teacher_runtime_id: Optional[str] = None

class BrainUpdatableProperties(BaseModel):
	name: Optional[str]
	description: Optional[str]
	temperature: Optional[float]
	model: Optional[str]
	max_tokens: Optional[int]
	openai_api_key: Optional[str]
	status: Optional[str]
	prompt_id: Optional[UUID]
	runtime_id: Optional[UUID]
	teacher_runtime_id: Optional[UUID]

	def dict(self, *args, **kwargs):
		brain_dict = super().model_dump(*args, **kwargs)
		if brain_dict.get("prompt_id"):
			brain_dict["prompt_id"] = str(brain_dict.get("prompt_id"))
		return brain_dict

class BrainInputRequest(BaseModel):
	chat_input: str

class ScoringMethod(str, enum.Enum):
	qa_correctness = "qa_correctness"
	fuzzy = "fuzzy"

class CreateBrainTestsuiteProperties(BaseModel):
	name: Optional[str] = "Default brain testsuite"
	scoring_method: ScoringMethod = ScoringMethod.qa_correctness

class UpdateBrainTestsuiteProperties(BaseModel):
	name: Optional[str] = "Default brain testsuite"
	scoring_method: ScoringMethod = ScoringMethod.qa_correctness

class CreateBrainTestcaseProperties(BaseModel):
	description: Optional[str] = "Default brain testcase"

class UpdateBrainTestcaseProperties(BaseModel):
	description: Optional[str] = "Default brain testcase"


class Brain(Repository):
	def __init__(self, supabase_client):
		self.db = supabase_client

	def create_brain(self, brain: CreateFullBrainProperties):
		response = (self.db.table("brains").insert(brain.model_dump())).execute()
		# convert runtime_id and teacher_runtime_id to string
		return BrainEntity(**response.data[0])

	def get_user_brains(self, user_id) -> list[FullBrainEntity]:
		response = (
			self.db.from_("brains_users")
			.select("id:brain_id, rights, brains (id, name, description, prompt_id, status, runtime_id, teacher_runtime_id)")
			.filter("user_id", "eq", user_id)
			.execute()
		)
		user_brains: list[FullBrainEntity] = []
		for item in response.data:
			runtime = get_runtime_by_id(item["brains"]["runtime_id"])
			teacher_runtime = get_runtime_by_id(item["brains"]["teacher_runtime_id"])
			user_brains.append(
				FullBrainEntity(
					id=item["brains"]["id"],
					name=item["brains"]["name"],
					description=item["brains"]["description"],
					status=item["brains"]["status"],
					prompt_id=item["brains"]["prompt_id"],
					runtime=runtime,
					teacher_runtime=teacher_runtime,
					last_update=item["brains"]["last_update"],
				)
			)
			user_brains[-1].rights = item["rights"]
		return user_brains

	def get_public_brains(self) -> list[PublicBrain]:
		response = (
			self.db.from_("brains")
			.select("id:brain_id, name, description, last_update")
			.filter("status", "eq", "public")
			.execute()
		)
		public_brains: list[PublicBrain] = []
		for item in response.data:
			brain = PublicBrain(
				id=item["id"],
				name=item["name"],
				description=item["description"],
				last_update=item["last_update"],
			)
			brain.number_of_subscribers = self.get_brain_subscribers_count(brain.id)
			public_brains.append(brain)
		return public_brains

	def update_brain_last_update_time(self, brain_id: UUID) -> None:
		self.db.table("brains").update({"last_update": "now()"}).match(
			{"brain_id": brain_id}
		).execute()

	def get_brain_for_user(self, user_id, brain_id) -> MinimalBrainEntity | None:
		response = (
			self.db.from_("brains_users")
			.select("id:brain_id, rights, brains (id: brain_id, status, name)")
			.filter("user_id", "eq", user_id)
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		if len(response.data) == 0:
			return None
		brain_data = response.data[0]

		return MinimalBrainEntity(
			id=brain_data["brains"]["id"],
			name=brain_data["brains"]["name"],
			rights=brain_data["rights"],
			status=brain_data["brains"]["status"],
		)

	def get_brain_details(self, brain_id):
		response = (
			self.db.from_("brains")
			.select("id:brain_id, name, *")
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		return response.data

	def delete_brain_user_by_id(
		self,
		user_id: UUID,
		brain_id: UUID,
	):
		results = (
			self.db.table("brains_users")
			.delete()
			.match({"brain_id": str(brain_id), "user_id": str(user_id)})
			.execute()
		)
		return results.data

	def delete_brain_vector(self, brain_id: str):
		results = (
			self.db.table("brains_vectors")
			.delete()
			.match({"brain_id": brain_id})
			.execute()
		)

		return results

	def delete_brain_users(self, brain_id: str):
		results = (
			self.db.table("brains_users")
			.delete()
			.match({"brain_id": brain_id})
			.execute()
		)

		return results

	def delete_brain_subscribers(self, brain_id: UUID):
		results = (
			self.db.table("brains_users")
			.delete()
			.match({"brain_id": str(brain_id)})
			.match({"rights": "Viewer"})
			.execute()
		).data

		return results

	def delete_brain(self, brain_id: str):
		results = (
			self.db.table("brains").delete().match({"brain_id": brain_id}).execute()
		)

		return results

	def create_brain_user(self, user_id: UUID, brain_id, rights, default_brain: bool):
		response = (
			self.db.table("brains_users")
			.insert(
				{
					"brain_id": str(brain_id),
					"user_id": str(user_id),
					"rights": rights,
					"default_brain": default_brain,
				}
			)
			.execute()
		)

		return response

	def create_brain_vector(self, brain_id, vector_id, file_sha1):
		response = (
			self.db.table("brains_vectors")
			.insert(
				{
					"brain_id": str(brain_id),
					"vector_id": str(vector_id),
					"file_sha1": file_sha1,
				}
			)
			.execute()
		)
		return response.data

	def get_vector_ids_from_file_sha1(self, file_sha1: str):
		# move to vectors class
		vectorsResponse = (
			self.db.table("vectors")
			.select("id")
			.filter("file_sha1", "eq", file_sha1)
			.execute()
		)
		return vectorsResponse.data

	def update_brain_by_id(
		self, brain_id: UUID, brain: BrainUpdatableProperties
	) -> BrainEntity | None:
		update_brain_response = (
			self.db.table("brains")
			.update(brain.dict(exclude_unset=True))
			.match({"brain_id": brain_id})
			.execute()
		).data

		if len(update_brain_response) == 0:
			return None

		return BrainEntity(**update_brain_response[0])

	def get_brain_vector_ids(self, brain_id):
		"""
		Retrieve unique brain data (i.e. uploaded files and crawled websites).
		"""

		response = (
			self.db.from_("brains_vectors")
			.select("vector_id")
			.filter("brain_id", "eq", brain_id)
			.execute()
		)

		vector_ids = [item["vector_id"] for item in response.data]

		if len(vector_ids) == 0:
			return []

		return vector_ids

	def delete_file_from_brain(self, brain_id, file_name: str):
		# First, get the vector_ids associated with the file_name
		vector_response = (
			self.db.table("vectors")
			.select("id")
			.filter("metadata->>file_name", "eq", file_name)
			.execute()
		)
		vector_ids = [item["id"] for item in vector_response.data]

		# For each vector_id, delete the corresponding entry from the 'brains_vectors' table
		for vector_id in vector_ids:
			self.db.table("brains_vectors").delete().filter(
				"vector_id", "eq", vector_id
			).filter("brain_id", "eq", brain_id).execute()

			# Check if the vector is still associated with any other brains
			associated_brains_response = (
				self.db.table("brains_vectors")
				.select("brain_id")
				.filter("vector_id", "eq", vector_id)
				.execute()
			)
			associated_brains = [
				item["brain_id"] for item in associated_brains_response.data
			]

			# If the vector is not associated with any other brains, delete it from 'vectors' table
			if not associated_brains:
				self.db.table("vectors").delete().filter(
					"id", "eq", vector_id
				).execute()

		return {"message": f"File {file_name} in brain {brain_id} has been deleted."}

	def get_default_user_brain_id(self, user_id: UUID) -> UUID | None:
		response = (
			(
				self.db.from_("brains_users")
				.select("brain_id")
				.filter("user_id", "eq", user_id)
				.filter("default_brain", "eq", True)
				.execute()
			)
		).data
		if len(response) == 0:
			return None
		return UUID(response[0].get("brain_id"))

	def get_brain_by_id(self, brain_id: UUID) -> BrainEntity | None:
		response = (
			self.db.from_("brains")
			.select("id, name, *")
			.filter("id", "eq", brain_id)
			.execute()
		).data

		if len(response) == 0:
			return None

		return BrainEntity(**response[0])

	def get_brain_subscribers_count(self, brain_id: UUID) -> int:
		response = (
			self.db.from_("brains_users")
			.select(
				"count",
			)
			.filter("brain_id", "eq", str(brain_id))
			.execute()
		).data
		if len(response) == 0:
			raise ValueError(f"Brain with id {brain_id} does not exist.")
		return response[0]["count"]
	
	def create_brain_meta_brain(self, brain_id: UUID, meta_brain_id):
		response = (
			self.db.table("brains_meta_brains")
			.insert(
				{
					"brain_id": str(brain_id),
					"meta_brain_id": str(meta_brain_id)
				}
			)
			.execute()
		)

		return response
	
	def get_brain_for_meta_brain(self, meta_brain_id) -> list[InfosBrainEntity] | None:
		response = (
			self.db.from_("brains_meta_brains")
			.select("id:brain_id, brains (id: brain_id, status, name, description, temperature, model, max_tokens, openai_api_key)")
			.filter("meta_brain_id", "eq", meta_brain_id)
			.execute()
		)
		infosbrains: list[InfosBrainEntity] = []
		for item in response.data:
			infosbrain = InfosBrainEntity(
				id=item["brains"]["id"],
				name=item["brains"]["name"],
				description=item["brains"]["description"],
				temperature=item["brains"]["temperature"],
				model=item["brains"]["model"],
				max_tokens=item["brains"]["max_tokens"],
				openai_api_key=item["brains"]["openai_api_key"]
			)
			infosbrains.append(infosbrain)
		return infosbrains
	
	def create_brain_testsuite_by_id(
		self, brain_id: UUID, 
		brain_testsuite: CreateBrainTestsuiteProperties
	) -> BrainTestSuiteEntity:
		response = (
			self.db.table("brain_testsuite")
			.insert(
				{
					"brain_id": str(brain_id),
					"name": brain_testsuite.name,
					"scoring_method": brain_testsuite.scoring_method
				}
			)
			.execute()
		)
		return BrainTestSuiteEntity(**response.data[0])
	
	def update_brain_testsuite_by_id(
		self, brain_id: UUID,
		brain_testsuite: UpdateBrainTestsuiteProperties
	) -> BrainTestSuiteEntity | None:
		response = (
			self.db.table("brain_testsuite")
			.update(brain_testsuite.model_dump(exclude_unset=True))
			.match({"brain_id": brain_id})
			.execute()
		).data

		if len(response) == 0:
			return None

		return BrainTestSuiteEntity(**response[0])
	
	def delete_brain_testsuite_by_id(self, brain_id: UUID):
		response = (
			self.db.table("brain_testsuite")
			.delete()
			.match({"brain_id": brain_id})
			.execute()
		)
		if len(response.data) == 0:
			return None
		return BrainTestSuiteEntity(**response.data[0])
	
	def get_brain_testsuite_by_id(self, brain_id: UUID) -> BrainTestSuiteEntity | None:
		response = (
			self.db.from_("brain_testsuite")
			.select("id:brain_id, brain_testsuite_id, name, scoring_method, last_update")
			.filter("brain_id", "eq", brain_id)
			.execute()
		).data

		if len(response) == 0:
			return None
		return BrainTestSuiteEntity(
			brain_id=response[0]["id"],
			brain_testsuite_id=response[0]["brain_testsuite_id"],
			name=response[0]["name"],
			scoring_method=response[0]["scoring_method"],
			last_update=response[0]["last_update"]
		)
	
	def update_brain_testsuite_last_update_time(self, brain_id: UUID) -> None:
		self.db.table("brain_testsuite").update({"last_update": "now()"}).match(
			{"brain_id": brain_id}
		).execute()
	
	def get_brain_testcase_by_testsuite_id(self, brain_testsuite_id: UUID) -> list[BrainTestCaseEntity]:
		response = (
			self.db.from_("brain_testcase")
			.select("id:brain_testcase_id, brain_testsuite_id, description, last_update")
			.filter("brain_testsuite_id", "eq", brain_testsuite_id)
			.execute()
		).data
		brain_testcases: list[BrainTestCaseEntity] = []
		for item in response:
			brain_testcase = BrainTestCaseEntity(
				brain_testcase_id=item["id"],
				brain_testsuite_id=item["brain_testsuite_id"],
				description=item["description"],
				last_update=item["last_update"]
			)
			brain_testcases.append(brain_testcase)
		return brain_testcases
	
	def create_brain_testcase_by_test_suite_id(
		self, brain_testsuite_id: UUID,
		brain_testcase: CreateBrainTestcaseProperties
	) -> BrainTestCaseEntity:
		response = (
			self.db.table("brain_testcase")
			.insert(
				{
					"brain_testsuite_id": str(brain_testsuite_id),
					"description": brain_testcase.description
				}
			)
			.execute()
		)
		return BrainTestCaseEntity(**response.data[0])
	
	def update_brain_testcase_by_test_suite_id(
		self, brain_testsuite_id: UUID, brain_testcase_id: UUID,
		brain_testcase: UpdateBrainTestcaseProperties
	) -> BrainTestCaseEntity | None:
		response = (
			self.db.table("brain_testcase")
			.update(brain_testcase.model_dump(exclude_unset=True))
			.match({"brain_testsuite_id": brain_testsuite_id, 
					"brain_testcase_id": brain_testcase_id})
			.execute()
		).data

		if len(response) == 0:
			return None

		return BrainTestCaseEntity(**response[0])
	
	def delete_brain_testcase_by_test_suite_id(
		self, brain_testsuite_id: UUID, brain_testcase_id: UUID
	) -> BrainTestCaseEntity:
		response = (
			self.db.table("brain_testcase")
			.delete()
			.match({"brain_testsuite_id": brain_testsuite_id, 
					"brain_testcase_id": brain_testcase_id})
			.execute()
		)
		if len(response.data) == 0:
			return None
		return BrainTestCaseEntity(**response.data[0])

	def get_scoring_method_from_brain_testsuite(self, brain_testsuite_id: UUID):
		response = (
			self.db.from_("brain_testsuite")
			.select("scoring_method")
			.filter("brain_testsuite_id", "eq", brain_testsuite_id)
			.execute()
		).data

		if len(response) == 0:
			return None

		return (response[0]["scoring_method"])
	
	def get_brain_testsuite_id_by_brain_id(self, brain_id: UUID):
		response = (
			self.db.from_("brain_testsuite")
			.select("brain_testsuite_id")
			.filter("brain_id", "eq", brain_id)
			.execute()
		).data

		if len(response) == 0:
			return None

		return (response[0]["brain_testsuite_id"])
	
	def create_brain_testrun_for_brain_testcase_id(
		self, brain_testcase_id: UUID, average_score: float
	):
		response = (
			self.db.table("brain_testrun")
			.insert(
				{
					"brain_testcase_id": str(brain_testcase_id),
					"average_score": average_score
				}
			)
			.execute()
		)
		return response
