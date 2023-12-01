from uuid import UUID

from app.models.settings import get_supabase_client
from app.modules.chat.service.chat_service import ChatService
from app.modules.test_data.entity.test_data import (MessageLabel,
                                                    MessageLabelOutput,
                                                    TestCaseDataEntity)
from app.modules.test_data.repository.test_data import TestData

chat_service = ChatService()


class TestDataService:
	repository: TestData

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = TestData(supabase_client)
	
	def get_message_label_by_id(self, message_id) -> MessageLabelOutput:
		return self.repository.get_message_label_by_id(message_id)
	
	def create_message_label_by_id(
		self,
		message_label: MessageLabel,
		message_id,
		user_id) -> MessageLabel | None:
		message_labeled = self.get_message_label_by_id(message_id)
		if message_labeled is None:
			return self.repository.create_message_label_by_id(
				message_label, message_id, user_id)
		else:
			return None
	
	def update_message_label_by_id(
		self, message_label: MessageLabel, message_id, user_id
	) -> MessageLabel:
		return self.repository.update_message_label_by_id(
			message_label, message_id, user_id)
	
	def delete_message_label_by_id(
		self, message_id, user_id
	):
		return self.repository.delete_message_label_by_id(
			message_id, user_id)

	def create_testcase_data_from_message(
		self,
		message_id: str,
		description: str,
	) -> TestCaseDataEntity:
		raw_message = chat_service.get_message_by_id(message_id)
		if raw_message is None:
			raise ValueError("Message not found")
		message_with_label = self.get_message_label_by_id(message_id)
		if message_with_label is None:
			raise ValueError("Message label not found")
		response = self.repository.create_testcase_data_from_message(
			description=description,
			input=raw_message.user_message,
			reference_output=message_with_label.label,
			context=message_with_label.feedback,
		)
		return TestCaseDataEntity(**response.data[0])
	
	def get_testcase_data_by_id(
		self, testcase_data_id: UUID) -> TestCaseDataEntity:
		return self.repository.get_testcase_data_by_id(testcase_data_id)
