import json
import os
from typing import Any, Optional
from uuid import UUID

from fastapi import UploadFile
from langchain.pydantic_v1 import Field
from langchain.schema import Document
from pydantic import BaseModel

from app.logger import get_logger

logger = get_logger(__name__)


class FileEntity(BaseModel):
	id: Optional[UUID] = None
	file: Optional[UploadFile]
	file_name: Optional[str] = ""
	file_size: Optional[int] = None
	file_sha1: Optional[str] = ""
	vectors_ids: Optional[list] = []
	file_extension: Optional[str] = ""
	content: Optional[Any] = None
	chunk_size: int = 500
	chunk_overlap: int = 0
	documents: Optional[Any] = None
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		if self.file:
			self.file_name = self.file.filename
			self.file_size = self.file.size  # pyright: ignore reportPrivateUsage=none
			self.file_extension = os.path.splitext(
				self.file.filename  # pyright: ignore reportPrivateUsage=none
			)[-1].lower()


class DocumentSerializable(Document):
	"""Class for storing a piece of text and associated metadata."""

	page_content: str
	metadata: dict = Field(default_factory=dict)

	@property
	def lc_serializable(self) -> bool:
		return True

	def __repr__(self):
		return f"Document(page_content='{self.page_content[:50]}...', metadata={self.metadata})"

	def __str__(self):
		return self.__repr__()

	def to_json(self) -> str:
		"""Convert the Document object to a JSON string."""
		return json.dumps(
			{
				"page_content": self.page_content,
				"metadata": self.metadata,
			}
		)

	@classmethod
	def from_json(cls, json_str: str):
		"""Create a Document object from a JSON string."""
		data = json.loads(json_str)
		return cls(page_content=data["page_content"], metadata=data["metadata"])
