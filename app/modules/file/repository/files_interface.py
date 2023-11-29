from abc import ABC, abstractmethod


class FilesInterface(ABC):
	@abstractmethod
	def upload_file_storage(self, file, file_identifier: str):
		pass