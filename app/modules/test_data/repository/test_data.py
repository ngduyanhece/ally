from uuid import UUID

from app.modules.test_data.entity.test_data import (MessageLabel,
                                                    MessageLabelOutput,
                                                    TestCaseDataEntity)
from app.modules.test_data.repository.test_data_interface import \
    TestDataInterface


class TestData(TestDataInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def create_testcase_data_from_message(
		self, description: str, input: str, reference_output: str, context: str):
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
			self, brain_testcase_id: UUID) -> list[TestCaseDataEntity]:
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
		self, dataset_id: UUID) -> list[TestCaseDataEntity]:
		response = (
			self.db.from_("datasets_testcase_data")
			.select("dataset_id, testcase_data (testcase_data_id, description, text_input, reference_output, context, last_update)")
			.filter("dataset_id", "eq", dataset_id)
			.execute()
		)
		testcase_data: list[TestCaseDataEntity] = []
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
	
	def get_testcase_data_by_id(
		self, testcase_data_id: UUID) -> TestCaseDataEntity:
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
	
	def create_message_label_by_id(
		self, message_label: MessageLabel, message_id, user_id
	) -> MessageLabel:
		response = (
			self.db.from_("label")
			.insert(
				{
					"message_id": str(message_id),
					"user_id": str(user_id),
					"label": message_label.label,
					"feedback": message_label.feedback,
				}
			)
			.execute()
		)

		return MessageLabel(**response.data[0])
	
	def update_message_label_by_id(
		self, message_label: MessageLabel, message_id, user_id
	) -> MessageLabel:
		response = (
			self.db.from_("label")
			.update(
				{
					"label": message_label.label,
					"feedback": message_label.feedback,
				}
			)
			.filter("message_id", "eq", message_id)
			.filter("user_id", "eq", user_id)
			.execute()
		)
		return MessageLabel(**response.data[0])
	
	def delete_message_label_by_id(
			self, message_id, user_id
	):
		response = (
			self.db.from_("label")
			.delete()
			.filter("message_id", "eq", message_id)
			.filter("user_id", "eq", user_id)
			.execute()
		)

		return response.data[0]
	
	def get_message_label_by_id(
		self, message_id: UUID) -> MessageLabelOutput | None:
		response = (
			self.db.from_("label")
			.select("*")
			.filter("message_id", "eq", message_id)
			.execute()
		).data
		if len(response) == 0:
			return None
		return MessageLabelOutput(**response[0])