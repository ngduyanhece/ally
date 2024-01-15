from modules.knowledge.repository.storage_interface import StorageInterface

from ally.core.settings import get_supabase_client
from ally.logger import get_logger

logger = get_logger(__name__)


class Storage(StorageInterface):
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client

	def upload_file(self, file_name: str):
		"""
		Upload file to storage
		"""
		self.db.storage.from_("ally").download(file_name)

	def remove_file(self, file_name: str):
		"""
		Remove file from storage
		"""
		try:
			response = self.db.storage.from_("ally").remove([file_name])
			return response
		except Exception as e:
			logger.error(e)
