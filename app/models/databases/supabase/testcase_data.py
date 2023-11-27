from typing import List
from uuid import UUID

from app.models.databases.repository import Repository
from app.models.testcase_data import TestCaseDataEntity


class TestCaseData(Repository):
	
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def create_testcase_data_from_message(self, description: str, input: str, reference_output: str, context: str):
		response = self.db.table("testcase_data"). \
			insert({
						"description": description,
						"text_input": input,
						"reference_output": reference_output,
						"context": context}).execute()
		return response
	
	def delete_testcase_data_by_id(self, testcase_data_id: str):
		response = self.db.table("testcase_data").delete().filter("testcase_data_id", "eq", testcase_data_id).execute()
		return response
	
	def add_testcase_data_to_brain_testcase(
			self, brain_testcase_id: UUID, testcase_data_id: UUID):
		response = self.db.table("brain_testcase_testcase_data").insert(
				{"brain_testcase_id": str(brain_testcase_id),
					"testcase_data_id": str(testcase_data_id)}).execute()
		return response
	
	def remove_testcase_data_to_brain_testcase(
			self, brain_testcase_id: UUID, testcase_data_id: UUID):
		response = self.db.table("brain_testcase_testcase_data").delete(). \
			filter("brain_testcase_id", "eq", str(brain_testcase_id)). \
			filter("testcase_data_id", "eq", str(testcase_data_id)).execute()
		return response

	def get_all_testcase_data_from_brain_testcase(
			self, brain_testcase_id: UUID) -> List[TestCaseDataEntity]:
		response = (
			self.db.from_("brain_testcase_testcase_data")
			.select("id:brain_testcase_id, testcase_data (id: testcase_data_id, description, input, reference_output, context, last_update)")
			.filter("brain_testcase_id", "eq", brain_testcase_id)
			.execute()
		)
		testcase_data = []
		for data in response.data:
			testcase_data.append(TestCaseDataEntity(
				testcase_data_id=data["testcase_data"]["id"],
				description=data["testcase_data"]["description"],
				input=data["testcase_data"]["input"],
				reference_output=data["testcase_data"]["reference_output"],
				context=data["testcase_data"]["context"],
				last_update=data["testcase_data"]["last_update"]
			))
		return testcase_data
	
	def get_all_testcase_data_from_a_dataset(
		self, dataset_id: UUID) -> List[TestCaseDataEntity]:
		response = (
			self.db.from_("datasets_testcase_data")
			.select("dataset_id, testcase_data (testcase_data_id, description, text_input, reference_output, context, last_update)")
			.filter("dataset_id", "eq", dataset_id)
			.execute()
		)
		testcase_data: List[TestCaseDataEntity] = []
		for data in response.data:
				testcase_data.append(TestCaseDataEntity(
					testcase_data_id=data["testcase_data"]["testcase_data_id"],
					description=data["testcase_data"]["description"],
					text_input=data["testcase_data"]["text_input"],
					reference_output=data["testcase_data"]["reference_output"],
					context=data["testcase_data"]["context"],
					chat_history="no chat history given",
					last_update=data["testcase_data"]["last_update"]
				))
		return testcase_data
	
	def get_testcase_data_by_id(self, testcase_data_id: UUID) -> TestCaseDataEntity:
		response = (
			self.db.from_("testcase_data")
			.select("id: testcase_data_id, description, text_input, reference_output, context, last_update")
			.filter("testcase_data_id", "eq", testcase_data_id)
			.execute()
		)
		testcase_data = TestCaseDataEntity(
			testcase_data_id=response.data[0]["id"],
			description=response.data[0]["description"],
			text_input=response.data[0]["text_input"],
			reference_output=response.data[0]["reference_output"],
			context=response.data[0]["context"],
			chat_history="no chat history given",
			last_update=response.data[0]["last_update"]
		)
		return testcase_data
