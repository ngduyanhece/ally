from abc import ABC, abstractmethod


class TestDataInterface(ABC):
	@abstractmethod
	def create_testcase_data_from_message(
		self, description: str, input: str, reference_output: str, context: str):
		pass