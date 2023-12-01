import os
import tempfile
import time
from uuid import UUID

from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.brain.service.brain_service import BrainService
from app.modules.file.entity.files import DocumentSerializable, FileEntity
from app.modules.file.repository.files import Files
from app.modules.knowledge.entity.knowledge import KnowledgeStatus
from app.modules.knowledge.service.knowledge_service import KnowledgeService
from app.modules.notification.service.notification_service import \
    NotificationService
from app.packages.embeddings.vectors import Neurons
from app.packages.files.file import compute_sha1_from_file
from app.packages.files.processors import FILE_PROCESSORS

logger = get_logger(__name__)
brain_service = BrainService()
notification_service = NotificationService()
knowledge_service = KnowledgeService()

def create_response(message, type):
	return {"message": message, "type": type}


class FileService:
	repository: Files
	message = ""

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Files(supabase_client)

	def upload_file_storage(self, file, file_identifier: str):
		return self.repository.upload_file_storage(file, file_identifier)
	
	async def compute_file_sha1(self, file: FileEntity):
		"""
		Compute the sha1 of the file using a temporary file
		"""
		with tempfile.NamedTemporaryFile(
			delete=False,
			suffix=file.file_name,
		) as tmp_file:
			await file.file.seek(0)
			file.content = (
				await file.file.read()  # pyright: ignore reportPrivateUsage=none
			)
			tmp_file.write(file.content)
			tmp_file.flush()
			file.file_sha1 = compute_sha1_from_file(tmp_file.name)

			os.remove(tmp_file.name)
	
	def compute_documents(self, loader_class, file: FileEntity):
		"""
		Compute the documents from the file

		Args:
			loader_class (class): The class of the loader to use to load the file
		"""
		logger.info(f"Computing documents from file {file.file_name}")

		documents = []
		with tempfile.NamedTemporaryFile(
			delete=False,
			suffix=file.file_name,  # pyright: ignore reportPrivateUsage=none
		) as tmp_file:
			tmp_file.write(file.content)  # pyright: ignore reportPrivateUsage=none
			tmp_file.flush()
			loader = loader_class(tmp_file.name)
			documents = loader.load()

		os.remove(tmp_file.name)

		text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
			chunk_size=file.chunk_size, chunk_overlap=file.chunk_overlap
		)

		file.documents = text_splitter.split_documents(documents)

	def set_file_vectors_ids(self, file: FileEntity):
		"""
		Set the vectors_ids property with the ids of the vectors
		that are associated with the file in the vectors table
		"""
		file.vectors_ids = self.repository.set_file_vectors_ids(
			file.file_sha1
		).data

	def file_already_exists(self, file: FileEntity):
		"""
		Check if file already exists in vectors table
		"""
		self.set_file_vectors_ids(file)

		# if the file does not exist in vectors then no need to go check in brains_vectors
		if len(file.vectors_ids) == 0:  # pyright: ignore reportPrivateUsage=none
			return False

		return True

	def file_already_exists_in_brain(self, brain_id, file: FileEntity):
		"""
		Check if file already exists in a brain

		Args:
				brain_id (str): Brain id
		"""
		response = self.repository.get_brain_vectors_by_brain_id_and_file_sha1(
			brain_id, file.file_sha1  # type: ignore
		)

		if len(response.data) == 0:
			return False

		return True

	def file_is_empty(self, file: FileEntity):
		"""
		Check if file is empty by checking if the file pointer is at the beginning of the file
		"""
		return file.file_size < 1  # pyright: ignore reportPrivateUsage=none

	def link_file_to_brain(self, brain_id: UUID, file: FileEntity):
		self.set_file_vectors_ids(file)

		if file.vectors_ids is None:
			return

		for vector_id in file.vectors_ids:  # pyright: ignore reportPrivateUsage=none
			brain_service.create_brain_vector(vector_id["id"], file.file_sha1, brain_id)

	def set_file_sha_from_metadata(self, file_sha1):
		self.repository.set_file_sha_from_metadata(file_sha1)
	
	async def filter_file(
		self,
		file: FileEntity,
		brain_id,
		original_file_name=None,
	):
		# compute compute_file_sha1
		await self.compute_file_sha1(file)

		file_exists = self.file_already_exists(file)
		file_exists_in_brain = self.file_already_exists_in_brain(brain_id, file)
		using_file_name = original_file_name or file.file_name if file.file else ""

		brain = brain_service.get_brain_details(brain_id)
		if brain is None:
			raise Exception("It seems like you're uploading knowledge to an unknown brain.")

		if file_exists_in_brain:
			self.message = create_response(
				f"🤔 {using_file_name} already exists in brain {brain.name}.",
				"warning",
			)
			return
		elif self.file_is_empty(file):
			self.message = create_response(
				f"❌ {original_file_name} is empty.",  # pyright: ignore reportPrivateUsage=none
				"error",  # pyright: ignore reportPrivateUsage=none
			)
			return
		elif file_exists:
			self.link_file_to_brain(brain_id, file)
			self.message = create_response(
				f"✅ {using_file_name} has been uploaded to brain {brain.name}.",  # pyright: ignore reportPrivateUsage=none
				"success",
			)
			return

		if file.file_extension in FILE_PROCESSORS:
			try:
				result = FILE_PROCESSORS[file.file_extension](
					self.process_file,
					file=file,
					brain_id=brain_id,
				)
				if result is None or result == 0:
					self.message = create_response(
						f"？ {using_file_name} has been uploaded to brain. There might have been an error while reading it, please make sure the file is not illformed or just an image",  # pyright: ignore reportPrivateUsage=none
						"warning",
					)
					return
				self.message = create_response(
					f"✅ {using_file_name} has been uploaded to brain {brain.name} in {result} chunks",  # pyright: ignore reportPrivateUsage=none
					"success",
				)
				return
			except Exception as e:
				# Add more specific exceptions as needed.
				print(f"Error processing file: {e}")
				self.message = create_response(
					f"⚠️ An error occurred while processing {using_file_name}.",  # pyright: ignore reportPrivateUsage=none
					"error",
				)
				return
		self.message = create_response(
			f"❌ {using_file_name} is not supported.",  # pyright: ignore reportPrivateUsage=none
			"error",
		)
		return
	
	def create_embedding_for_document(
		self, brain_id, doc_with_metadata, file_sha1):
		neurons = Neurons()
		doc = DocumentSerializable.from_json(doc_with_metadata)
		created_vector = neurons.create_vector(doc)
		self.set_file_sha_from_metadata(file_sha1)

		created_vector_id = created_vector[0]
		brain_service.create_brain_vector(brain_id, created_vector_id, file_sha1)

	def process_file(
		self,
		file: FileEntity,
		loader_class,
		brain_id,
	):
		dateshort = time.strftime("%Y%m%d")

		self.compute_documents(loader_class, file)

		for doc in file.documents:
			metadata = {
				"file_sha1": file.file_sha1,
				"file_size": file.file_size,
				"file_name": file.file_name,
				"chunk_size": file.chunk_size,
				"chunk_overlap": file.chunk_overlap,
				"date": dateshort,
			}
			doc_with_metadata = DocumentSerializable(
				page_content=doc.page_content, metadata=metadata
			)

			self.create_embedding_for_document(
				brain_id, doc_with_metadata.to_json(), file.file_sha1
			)

		return len(file.documents)
	
	async def process_file_and_notify(
		self,
		file_name: str,
		file_original_name: str,
		brain_id,
		knowledge_id=None,
	):
		try:
			tmp_file_name = "tmp-file-" + file_name
			tmp_file_name = tmp_file_name.replace("/", "_")

			with open(tmp_file_name, "wb+") as f:
				res = self.repository.download_file_from_storage(file_name)
				f.write(res)
				f.seek(0)
				file_content = f.read()

				upload_file = UploadFile(
					file=f, filename=file_name.split("/")[-1], size=len(file_content)
				)

				file_instance = FileEntity(file=upload_file)
				await self.filter_file(
					file=file_instance,
					brain_id=brain_id,
					original_file_name=file_original_name,
				)
				f.close()
				os.remove(tmp_file_name)

				if knowledge_id:
					notification_message = {
						"status": self.message["type"],
						"message": self.message["message"],
						"name": file_instance.file.filename if file_instance.file else "",
					}
					knowledge_service.update_knowledge_property_by_id(
						knowledge_id, {"status": KnowledgeStatus.Done}
					)
					knowledge_service.update_knowledge_property_by_id(
						knowledge_id, {"message": str(notification_message)}
					)
					# notification_service.update_notification_by_id(
					# 	notification_id, UpdateNotificationProperties(
					# 		status=NotificationsStatusEnum.Done,
					# 		message=str(notification_message),
					# 	),
					# )
				brain_service.update_brain_last_update_time(brain_id)

				return True
		except Exception as e:
			notification_message = {
				"status": "error",
				"message": "There was an error uploading the file. Please check the file and try again. If the issue persist, please open an issue on Github",
				"name": file_instance.file.filename if file_instance.file else "",
			}
			# notification_service.update_notification_by_id(
			# 	notification_id, UpdateNotificationProperties(
			# 		status=NotificationsStatusEnum.Done,
			# 		message=str(notification_message),
			# 	),
			# )
			knowledge_service.update_knowledge_property_by_id(
				knowledge_id, {"status": KnowledgeStatus.Error}
			)
			knowledge_service.update_knowledge_property_by_id(
				knowledge_id, {"message": str(notification_message)}
			)
			raise e

	def delete_file_from_storage(self, file_identifier: str):
		return self.repository.delete_file_from_storage(file_identifier)
